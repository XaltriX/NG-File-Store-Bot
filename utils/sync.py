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
from utils.ui import kb

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
    for o in await db.sync_unsent(50):
        await box.update_one(
            {'_id': o['_id']},
            {'$setOnInsert': {'src': my_id, 'u': o['u'], 'days': o['days'], 'ts': o['ts'], 'done_by': []}},
            upsert=True
        )
        await db.sync_mark_sent(o['_id'])


async def pull_incoming(client, box, settings):
    my_id = client.me.id
    now = int(time.time())
    query = {'src': {'$ne': my_id}, 'done_by': {'$ne': my_id}, 'ping': {'$ne': True},
             'ts': {'$gt': now - KEEP_DAYS * 86400}}
    for d in await box.find(query).limit(50).to_list(50):
        claimed = await box.find_one_and_update(
            {'_id': d['_id'], 'done_by': {'$ne': my_id}}, {'$addToSet': {'done_by': my_id}})
        if not claimed:
            continue
        try:
            exp = await db.extend_premium(d['u'], int(d['days']))
            await db.bump_stat('prem_synced')
        except Exception:
            await box.update_one({'_id': d['_id']}, {'$pull': {'done_by': my_id}})  # retry next round
            raise
        user = await db.get_user(d['u']) or {}
        lang = user.get('lang') or 'en'
        plan = f"{d['days']} दिन" if lang == 'hi' else f"{d['days']} days"
        rows = contact_row(settings, lang)
        try:
            await client.send_message(d['u'], tr(lang, 'approved', plan=plan, date=ist_str(exp)),
                                      reply_markup=kb(rows) if rows else None, parse_mode=ParseMode.HTML)
        except Exception:
            pass  # user never started this bot or blocked it: premium is still active


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
    await asyncio.sleep(20)
    fails, alerted, last_clean, last_write = 0, False, 0, 0
    while True:
        try:
            s = await db.get_settings()
            if s.get('sync_enabled') and s.get('sync_url'):
                try:
                    box = mailbox(s)
                    await push_pending(client, box)
                    await pull_incoming(client, box, s)
                    now = int(time.time())
                    if now - last_clean > 3600:
                        await box.delete_many({'ts': {'$lt': now - KEEP_DAYS * 86400}})
                        await db.sync_cleanup(now - KEEP_DAYS * 86400)
                        last_clean = now
                    if now - last_write > 60 or s.get('sync_err'):
                        await db.update_settings('sync_last_ok', now)
                        await db.update_settings('sync_err', '')
                        last_write = now
                    if alerted:
                        alerted = False
                        try:
                            await client.send_message(Config.OWNER_ID, "✅ <b>Partner sync is back.</b>\nPending premium grants were delivered.", parse_mode=ParseMode.HTML)
                        except Exception:
                            pass
                    fails = 0
                except Exception as e:
                    fails += 1
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
