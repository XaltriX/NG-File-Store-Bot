"""Safety net for the background workers + records user activity (used by the inactivity reminders)."""
from pyrogram import Client, filters
from utils.background import ensure_background
from utils.database import db


@Client.on_message(filters.private, group=-100)
async def _boot_on_message(client, message):
    ensure_background(client)
    if message.from_user:
        try:
            await db.touch(message.from_user.id)
        except Exception:
            pass


@Client.on_callback_query(group=-100)
async def _boot_on_callback(client, query):
    ensure_background(client)
    try:
        await db.touch(query.from_user.id)
    except Exception:
        pass
