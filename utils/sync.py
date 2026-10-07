"""
Partner-bot sync through a shared 'mailbox' MongoDB.

Both bots use the SAME mailbox URL + DB name. When premium is granted in one bot, a small
note is left in the mailbox; the other bot reads it, grants premium itself and notifies the
user in the user's own language. Only GRANTS are synced (never removals).
"""
import asyncio
import time
import motor.motor_asyncio
from pyrogram.enums import ParseMode
from config import Config
from utils.database import db
from utils.helpers import ist_str
from utils.i18n import tr
from utils.prem import contact_row
from utils.ui import kb, more_row
from utils import referral

KEEP_DAYS = 7
LOOP_SECONDS = 15
_clients = {}


def host_of(url):
    return (url or "").split('@')[-1].split('/')[0].split('?')[0] or "not set"


def mailbox(settings):
    url = settings.get('sync_url')
    if not url:
        return None
    name = settings.get('sync_db') or 'sync_mailbox'
    cli = _clients.get(url)
    if cli is None:
        cli = _clients[url] = motor.motor_asyncio.AsyncIOMotorClient(url, serverSelectionTimeoutMS=8000)
    return cli[name]['sync_inbox']


def forget_client(url=None):
    for key in ([url] if url else list(_clients)):
        cli = _clients.pop(key, None)
        if cli:
            try:
                cli.close()
            except Exception:
                pass


async def push_pending(client, box):
    my_id = client.me.id
    n = 0
    for o in await db.sync_unsent(50):
        fields = {k: v for k, v in o.items() if k not in ('_id', 'sent', 'sent_at')}
        fields.update({'src': my_id, 'done_by': []})
        await box.update_one({'_id': o['_id']}, {'$setOnInsert': fields}, upsert=True)
        await db.sync_mark_sent(o['_id'])
        n += 1
    return n


async def pull_incoming(client, box, settings):
    my_id = client.me.id
    now = int(time.time())
    applied = 0
    query = {'src': {'$ne': my_id}, 'done_by': {'$ne': my_id}, 'ping': {'$ne': True},
             'ts': {'$gt': now - KEEP_DAYS * 86400}}
    for d in await box.find(query).sort([('ts', 1), ('_id', 1)]).limit(50).to_list(50):
        claimed = await box.find_one_and_update(
            {'_id': d['_id'], 'done_by': {'$ne': my_id}}, {'$addToSet': {'done_by': my_id}})
        if not claimed:
            continue
        kind = d.get('kind')
        try:
            if kind == 'ref':                       # a referral that happened in the partner bot
                await referral.apply_remote_event(client, d, settings)
            elif kind == 'refq':                    # that referred user received a file there
                await db.qualify_referral(d['u'])
            else:
                exp = await db.extend_premium(d['u'], int(d['days']))
                await db.bump_stat('prem_synced')
        except Exception:
            await box.update_one({'_id': d['_id']}, {'$pull': {'done_by': my_id}})  # retry next round
            raise
        applied += 1
        if kind in ('ref', 'refq'):
            continue
        print(f"🔁 Sync: granted {d['days']} day(s) premium to {d['u']} (from partner bot)")
        user = await db.get_user(d['u']) or {}
        lang = user.get('lang') or 'en'
        plan = f"{d['days']} दिन" if lang == 'hi' else f"{d['days']} days"
        rows = contact_row(settings, lang) + more_row(settings, lang)
        try:
            await client.send_message(d['u'], tr(lang, 'approved', plan=plan, date=ist_str(exp)),
                                      reply_markup=kb(rows) if rows else None, parse_mode=ParseMode.HTML)
        except Exception:
            pass  # user never started this bot or blocked it: premium is still active
    return applied


async def sync_once(client, force=False):
    """One full round: send my pending grants, read the partner's, leave a heartbeat. Returns (sent, received)."""
    s = await db.get_settings()
    if not s.get('sync_url'):
        raise ValueError("Set the Mailbox URL first.")
    if not (force or s.get('sync_enabled')):
        return 0, 0
    box = mailbox(s)
    my_id = client.me.id
    pushed = await push_pending(client, box)
    pulled = await pull_incoming(client, box, s)
    await box.update_one(
        {'_id': f'hb_{my_id}'},
        {'$set': {'hb': True, 'ping': True, 'src': my_id, 'ts': int(time.time()), 'done_by': [my_id]}},
        upsert=True
    )
    if pushed:
        print(f"🔁 Sync: sent {pushed} premium grant(s) to the mailbox")
    return pushed, pulled


async def push_now(client):
    """Best effort right after an approval so the partner does not wait for the next round."""
    try:
        s = await db.get_settings()
        if not (s.get('sync_enabled') and s.get('sync_url')):
            return 0
        return await push_pending(client, mailbox(s))
    except Exception as e:
        print(f"Sync push_now will retry later: {type(e).__name__}")
        return 0


async def partner_seen(settings):
    """Unix time of the partner bot's last heartbeat, 0 = never seen, None = unknown/unreachable."""
    me = settings.get('my_bot_id')
    if not (settings.get('sync_url') and me):
        return None
    try:
        box = mailbox(settings)
        d = await asyncio.wait_for(box.find_one({'hb': True, 'src': {'$ne': me}}, sort=[('ts', -1)]), 4)
        return d.get('ts', 0) if d else 0
    except Exception:
        return None


async def test_connection(client):
    s = await db.get_settings()
    try:
        box = mailbox(s)
        if box is None:
            return False, "Set the Mailbox URL first."
        ref = f"ping_{client.me.id}"
        await box.update_one({'_id': ref}, {'$set': {'ts': int(time.time()), 'src': client.me.id,
                                                       'ping': True, 'done_by': [client.me.id]}}, upsert=True)
        got = await box.find_one({'_id': ref})
        await box.delete_one({'_id': ref})
        if got:
            return True, "Connected. Read and write both work."
        return False, "Write worked but read failed."
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:120]}"


async def sync_loop(client):
    print("🔁 Sync worker started")
    await asyncio.sleep(10)
    fails, alerted, last_clean, last_tick = 0, False, 0, 0
    while True:
        try:
            s = await db.get_settings()
            now = int(time.time())
            if now - last_tick >= 30:                      # heartbeat so the panel can show "worker running"
                await db.update_settings('sync_tick', now)
                if s.get('my_bot_id') != client.me.id:
                    await db.update_settings('my_bot_id', client.me.id)
                last_tick = now
            if s.get('sync_enabled') and s.get('sync_url'):
                try:
                    await sync_once(client)
                    if now - last_clean > 3600:
                        await mailbox(s).delete_many({'ts': {'$lt': now - KEEP_DAYS * 86400}})
                        await db.sync_cleanup(now - KEEP_DAYS * 86400)
                        last_clean = now
                    if s.get('sync_err'):
                        await db.update_settings('sync_err', '')
                    await db.update_settings('sync_last_ok', now) if now - (s.get('sync_last_ok') or 0) > 60 else None
                    if alerted:
                        alerted = False
                        try:
                            await client.send_message(Config.OWNER_ID, "✅ <b>Partner sync is back.</b>\nPending premium grants were delivered.", parse_mode=ParseMode.HTML)
                        except Exception:
                            pass
                    fails = 0
                except Exception as e:
                    fails += 1
                    print(f"🔁 Sync error ({fails}): {type(e).__name__}: {str(e)[:120]}")
                    await db.update_settings('sync_err', f"{type(e).__name__}: {str(e)[:100]}")
                    if fails >= 3 and not alerted:
                        alerted = True
                        try:
                            await client.send_message(
                                Config.OWNER_ID,
                                "⚠️ <b>Partner sync problem</b>\n\nCannot reach the shared mailbox, so premium given here "
                                "is NOT reaching the partner bot yet. It will retry automatically.\n"
                                f"<code>{type(e).__name__}</code>\nCheck Admin Panel → Trial & Premium → Partner bot → Test connection.",
                                parse_mode=ParseMode.HTML)
                        except Exception:
                            pass
            else:
                fails = 0
        except Exception as e:
            print(f"Sync loop error: {e}")
        await asyncio.sleep(LOOP_SECONDS)
