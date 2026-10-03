import threading
import asyncio
import uvloop
from pyrogram import Client
from config import Config
from server import keep_alive
from utils.database import db
from utils.background import ensure_background

# 🚀 Uvloop: The Ultimate CPU & RAM Engine
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

plugins = dict(root="plugins")

app = Client(
    "AdvancedFileStore",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=plugins,
    sleep_threshold=30,
    max_concurrent_transmissions=5
)

# Start the reminder / expiry-notice scheduler right after the client connects
_orig_start = app.start


async def _start_with_scheduler(*args, **kwargs):
    result = await _orig_start(*args, **kwargs)
    ensure_background(app)
    return result

app.start = _start_with_scheduler

async def setup_indexes():
    try:
        await db.files_col1.create_index([("_id", 1)])
        if db.files_col2:
            await db.files_col2.create_index([("_id", 1)])
        if db.files_col3:
            await db.files_col3.create_index([("_id", 1)])
            
        await db.tokens_col.create_index("createdAt", expireAfterSeconds=86400)
        await db.vlog_col.create_index("date")
        await db.users_col.create_index("trial_start", sparse=True)
        await db.premium_col.create_index("expire_at")
        await db.pay_col.create_index([("u", 1), ("status", 1)])
        await db.users_col.create_index("ever_premium", sparse=True)
        await db.users_col.create_index("ever_verified", sparse=True)
        try:
            await db.backfill_flags()
        except Exception as e:
            print(f"Flag backfill skipped: {e}")
        print("⚡ MongoDB Auto-Indexing & TTL Complete!")
    except Exception as e:
        print(f"Indexing Error: {e}")

if __name__ == "__main__":
    print("🌐 Starting Zero-RAM Health Server...")
    threading.Thread(target=keep_alive, daemon=True).start()
    
    # 🚀 Safe Loop Initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_indexes())
    
    print("🚀 Advanced Bot is Starting with Kurigram!")
    app.run()
