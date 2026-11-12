import asyncio
import time
from config import Config
from utils.database import db
from utils.helpers import ist_date, ist_now


async def run_cleanup(client=None, alert=True):
    """Delete old records, remember the result, and warn the owner when the database is nearly full."""
    res = await db.cleanup()
    used, limit = await db.storage_used_mb()
    await db.update_settings('last_cleanup', {'ts': int(time.time()), 'res': res})
    if alert and client and limit and used / limit >= 0.8:
        s = await db.get_settings()
        if s.get('storage_alert_date') != ist_date():
            await db.update_settings('storage_alert_date', ist_date())
            try:
                await client.send_message(
                    Config.OWNER_ID,
                    f"⚠️ <b>Storage almost full</b>\n\n<blockquote>Database: <b>{used:.0f} / {limit} MB</b> "
                    f"({used * 100 / limit:.0f}%)</blockquote>\nOpen Admin → Stats → 🧹 Storage.")
            except Exception:
                pass
    return res


async def cleanup_loop(client):
    """Once a day after 3 AM IST."""
    await asyncio.sleep(120)
    while True:
        try:
            s = await db.get_settings()
            if ist_now().hour >= 3 and (s.get('last_cleanup_date') != ist_date()):
                await db.update_settings('last_cleanup_date', ist_date())
                await run_cleanup(client)
        except Exception as e:
            print(f"Cleanup error: {e}")
        await asyncio.sleep(1800)
