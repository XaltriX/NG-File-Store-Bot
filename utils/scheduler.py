import asyncio
import math
import time
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from utils.database import db
from utils.helpers import ist_now, ist_str
from utils.i18n import tr, REMINDER_EN, REMINDER_HI
from utils.ui import btn, kb

BLOCKED = {'UserIsBlocked', 'InputUserDeactivated', 'UserDeactivated', 'UserDeactivatedBan', 'PeerIdInvalid'}
CHECK_EVERY = 600  # seconds


def in_quiet_hours(settings):
    if not settings.get('quiet_hours', True):
        return False
    hour = ist_now().hour
    return hour >= 23 or hour < 8


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
                text = settings.get('reminder_text_hi' if lang == 'hi' else 'reminder_text') \
                    or (REMINDER_HI if lang == 'hi' else REMINDER_EN)
                if u.get('rem_msg'):
                    try:
                        await client.delete_messages(uid, u['rem_msg'])
                    except Exception:
                        pass
                markup = kb([[
                    btn(tr(lang, 'b_verify'), url=f"https://t.me/{bot_username}?start=getverify"),
                    btn(tr(lang, 'b_premium'), "prem_open"),
                ]])
                m = await client.send_message(uid, text, reply_markup=markup, parse_mode=ParseMode.HTML)
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
                reply_markup=kb([[btn(tr(lang, 'b_renew'), "prem_open")]]), parse_mode=ParseMode.HTML
            )
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            continue
        except Exception:
            pass
        await db.mark_prem_notified(uid, flags)
        await asyncio.sleep(0.05)


async def reminder_loop(client):
    await asyncio.sleep(30)
    while True:
        try:
            settings = await db.get_settings()
            if not in_quiet_hours(settings):
                await run_expiry_notices(client)
                if settings.get('reminder_enabled', True) and settings.get('shortlink_status'):
                    await run_reminders(client, settings)
        except Exception as e:
            print(f"Scheduler error: {e}")
        await asyncio.sleep(CHECK_EVERY)
