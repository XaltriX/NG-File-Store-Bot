from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from utils.database import db

@Client.on_chat_join_request()
async def handle_join_request(client: Client, request: ChatJoinRequest):
    # 🚀 Save the request instantly so the user gets the file even before approval
    await db.add_join_request(request.from_user.id, request.chat.id)
