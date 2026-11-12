import asyncio
from utils.database import db
from utils.scheduler import reminder_loop
from utils.sync import sync_loop
from utils.referral import referral_loop
from utils.cleanup import cleanup_loop

_started = False


def ensure_background(client):
    """Start the reminder and sync workers exactly once. Safe to call from anywhere inside the running loop."""
    global _started
    db.ensure_loop()
    if _started or not getattr(client, "me", None):
        return
    _started = True
    loop = asyncio.get_running_loop()
    loop.create_task(reminder_loop(client))
    loop.create_task(sync_loop(client))
    loop.create_task(referral_loop(client))
    loop.create_task(cleanup_loop(client))
    print("🚀 Background workers started (reminders, partner sync, referral prizes, storage cleanup)")
