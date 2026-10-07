import asyncio
from utils.scheduler import reminder_loop
from utils.sync import sync_loop
from utils.referral import referral_loop

_started = False


def ensure_background(client):
    """Start the reminder and sync workers exactly once. Safe to call from anywhere inside the running loop."""
    global _started
    if _started or not getattr(client, "me", None):
        return
    _started = True
    loop = asyncio.get_running_loop()
    loop.create_task(reminder_loop(client))
    loop.create_task(sync_loop(client))
    loop.create_task(referral_loop(client))
    print("🚀 Background workers started (reminders, partner sync, weekly referral prizes)")
