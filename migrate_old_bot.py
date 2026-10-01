"""
Copy data from an old Codeflix-style bot (rohit_1888) into this bot's format.

SAFE: old collections are only READ, never changed or deleted.
Default is a DRY RUN (shows what it would do). Add --apply to really write.

  python migrate_old_bot.py              # dry run
  python migrate_old_bot.py --apply      # copy premium users + banned users
  python migrate_old_bot.py --apply --fsub   # also copy force-sub channel IDs

Uses MONGO_URI_1 and MONGO_DB_NAME from your .env (the DB that holds the old data).
"""
import os
import sys
import asyncio
from datetime import datetime
import motor.motor_asyncio
from dotenv import load_dotenv


def to_epoch(iso):
    try:
        return int(datetime.fromisoformat(iso).timestamp())
    except Exception:
        return 0


def sample(doc):
    return {k: type(v).__name__ for k, v in (doc or {}).items()}


async def migrate(db, apply=False, fsub=False, now=None, out=print):
    import time
    now = now or int(time.time())
    report = {'premium': 0, 'premium_expired': 0, 'banned': 0, 'fsub': 0}

    # ---- premium: old 'premium-users' {user_id, expiration_timestamp ISO}  ->  'premium_users' {_id, expire_at epoch}
    async for d in db['premium-users'].find({}):
        uid, exp = d.get('user_id'), to_epoch(d.get('expiration_timestamp', ''))
        if not isinstance(uid, int) or not exp:
            continue
        if exp <= now:
            report['premium_expired'] += 1
            continue
        cur = await db['premium_users'].find_one({'_id': uid})
        if cur and cur.get('expire_at', 0) >= exp:
            continue
        report['premium'] += 1
        if apply:
            await db['premium_users'].update_one(
                {'_id': uid},
                {'$set': {'expire_at': exp, 'daily_limit': 0, 'used_today': 0, 'last_date': '', 'n3': False, 'n1': False}},
                upsert=True)

    # ---- banned: old 'banned_user' -> 'banned_users'
    async for d in db['banned_user'].find({}):
        uid = d.get('_id') if isinstance(d.get('_id'), int) else d.get('user_id')
        if not isinstance(uid, int):
            continue
        report['banned'] += 1
        if apply:
            await db['banned_users'].update_one({'_id': uid}, {'$set': {'banned': True}}, upsert=True)

    # ---- force-sub channel IDs (opt-in, structure of the old collections is not guaranteed)
    ids = set()
    for name in ('fsub', 'channels'):
        first = await db[name].find_one({})
        out(f"  [{name}] sample fields: {sample(first)}")
        async for d in db[name].find({}):
            for key in ('_id', 'channel_id', 'chat_id'):
                v = d.get(key)
                if isinstance(v, int) and v < -1000000000:
                    ids.add(v)
    report['fsub'] = len(ids)
    if fsub and apply and ids:
        await db['settings'].update_one({'_id': 'bot_settings'}, {'$addToSet': {'fsub_channels': {'$each': sorted(ids)}}}, upsert=True)
    if ids:
        out(f"  force-sub channel IDs found: {sorted(ids)}")
    return report


async def main():
    load_dotenv()
    apply, fsub = '--apply' in sys.argv, '--fsub' in sys.argv
    uri, name = os.environ.get('MONGO_URI_1'), os.environ.get('MONGO_DB_NAME', 'filestorebot')
    if not uri:
        raise SystemExit("Set MONGO_URI_1 (and MONGO_DB_NAME) in .env first.")
    db = motor.motor_asyncio.AsyncIOMotorClient(uri)[name]
    print(f"{'APPLYING' if apply else 'DRY RUN'} on database '{name}'")
    r = await migrate(db, apply, fsub)
    print(f"premium to copy: {r['premium']} (already expired, skipped: {r['premium_expired']})")
    print(f"banned users to copy: {r['banned']}")
    print(f"force-sub IDs found: {r['fsub']}" + ("  (copied)" if fsub and apply else "  (use --apply --fsub to copy)"))
    if not apply:
        print("\nNothing was written. Run again with --apply to copy.")


if __name__ == '__main__':
    asyncio.run(main())
