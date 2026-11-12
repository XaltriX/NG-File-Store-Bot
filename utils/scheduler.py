import asyncio
import math
import time
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from utils.database import db
from utils.helpers import ist_str
from utils.i18n import tr
from utils.ui import btn, kb, more_row

BLOCKED = {'UserIsBlocked', 'InputUserDeactivated', 'UserDeactivated', 'UserDeactivatedBan', 'PeerIdInvalid'}
CHECK_EVERY = 600  # seconds


def style_reminder(text):
    """Title stays bold on top, the message goes into a quote block."""
    if '<blockquote' in text:
        return text
    head, sep, body = text.partition('\n\n')
    return f"{head}\n\n<blockquote>{body}</blockquote>" if sep else f"<blockquote>{text}</blockquote>"


def build_reminder(settings, lang, bot_username):
    custom = settings.get('reminder_text_hi' if lang == 'hi' else 'reminder_text') if lang in ('en', 'hi') else None
    text = style_reminder(custom or tr(lang, 'reminder'))
    markup = kb([[
        btn(tr(lang, 'b_verify'), url=f"https://t.me/{bot_username}?start=getverify", color='green'),
        btn(tr(lang, 'b_premium'), "prem_open", color='blue'),
    ]] + more_row(settings, lang))
    return text, markup


async def send_reminder(client, uid, text, markup, media=None):
    """Photo / video / GIF with the text as caption; plain text if there is no media or it fails."""
    if media:
        try:
            send = getattr(client, 'send_' + media['t'])
            return await send(uid, media['f'], caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
        except FloodWait:
            raise
        except Exception as e:
            if type(e).__name__ in BLOCKED:
                raise
    return await client.send_message(uid, text, reply_markup=markup, parse_mode=ParseMode.HTML)


async def _is_verified(uid, user, settings):
    if settings.get('shortlink_type') == 'credit':
        return user.get('credits', 0) > 0
    return bool(await db.verified_expire(uid))


async def run_reminders(client, settings):
    bot_username = client.me.username if client.me else (await client.get_me()).username
    while True:
        users = await db.reminder_candidates(settings, 50)
        if not users:
            break
        for u in users:
            uid = u['_id']
            try:
                if await db.premium_expire(uid) or await _is_verified(uid, u, settings) or await db.is_banned(uid):
                    await db.mark_checked(uid)
                    continue
                lang = u.get('lang') or 'en'
                text, markup = build_reminder(settings, lang, bot_username)
                pool = settings.get('rem_media') or []
                media = pool[u.get('rem_idx', 0) % len(pool)] if pool else None
                if u.get('rem_msg'):
                    try:
                        await client.delete_messages(uid, u['rem_msg'])
                    except Exception:
                        pass
                m = await send_reminder(client, uid, text, markup, media)
                await db.mark_reminded(uid, m.id)
                await db.bump_stat('reminders_sent')
            except FloodWait as e:
                await asyncio.sleep(e.value + 1)
            except Exception as e:
                if type(e).__name__ in BLOCKED:
                    await db.mark_reminder_off(uid)
                else:
                    await db.mark_checked(uid)
            await asyncio.sleep(0.05)
        if len(users) < 50:
            break


async def run_expiry_notices(client):
    now = int(time.time())
    settings = await db.get_settings()
    for doc in await db.premium_expiring():
        left = doc['expire_at'] - now
        if left <= 86400 and not doc.get('n1'):
            flags, days = ['n1', 'n3'], 1
        elif left <= 3 * 86400 and not doc.get('n3'):
            flags, days = ['n3'], max(1, math.ceil(left / 86400))
        else:
            continue
        uid = doc['_id']
        user = await db.get_user(uid) or {}
        lang = user.get('lang') or 'en'
        try:
            await client.send_message(
                uid, tr(lang, 'exp_soon', days=days, date=ist_str(doc['expire_at'])),
                reply_markup=kb([[btn(tr(lang, 'b_renew'), "prem_open")]] + more_row(settings, lang)), parse_mode=ParseMode.HTML
            )
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            continue
        except Exception:
            pass
        await db.mark_prem_notified(uid, flags)
        await asyncio.sleep(0.05)


async def run_winback(client):
    """1 and 3 days after Premium ends: one friendly message each, with Renew + More Videos."""
    now = int(time.time())
    settings = await db.get_settings()
    for doc in await db.winback_due():
        ago = now - doc['expire_at']
        if ago >= 3 * 86400 and not doc.get('w3'):
            flags, days = ['w1', 'w3'], 3
        elif ago >= 86400 and not doc.get('w1') and ago < 3 * 86400:
            flags, days = ['w1'], 1
        else:
            continue
        uid = doc['_id']
        lang = ((await db.get_user(uid)) or {}).get('lang') or 'en'
        try:
            await client.send_message(
                uid, tr(lang, 'winback', days=days),
                reply_markup=kb([[btn(tr(lang, 'b_renew'), "prem_open")]] + more_row(settings, lang)), parse_mode=ParseMode.HTML)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            continue
        except Exception:
            pass
        await db.mark_prem_notified(uid, flags)
        await asyncio.sleep(0.05)
    await db.winback_cleanup()


async def reminder_loop(client):
    await asyncio.sleep(30)
    try:
        await db.backfill_activity()
    except Exception as e:
        print(f"Activity backfill error: {e}")
    while True:
        try:
            settings = await db.get_settings()
            await run_expiry_notices(client)
            await run_winback(client)
            if settings.get('reminder_enabled', True) and settings.get('shortlink_status'):
                await run_reminders(client, settings)
        except Exception as e:
            print(f"Scheduler error: {e}")
        await asyncio.sleep(CHECK_EVERY)
