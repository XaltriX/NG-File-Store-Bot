"""Safety net: if the start hook did not launch the background workers, the first update does."""
from pyrogram import Client, filters
from utils.background import ensure_background


@Client.on_message(filters.private, group=-100)
async def _boot_on_message(client, message):
    ensure_background(client)


@Client.on_callback_query(group=-100)
async def _boot_on_callback(client, query):
    ensure_background(client)
