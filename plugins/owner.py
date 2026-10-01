from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from utils.database import db
from script import Script

@Client.on_message(filters.command("add_admin") & filters.private)
async def add_new_admin(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return await message.reply_text("⚠️ **Warning:** You are not the bot owner! Only the owner can add new admins.")

    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/add_admin UserID`")
        
    try:
        user_id = int(message.command[1])
        success = await db.add_admin(user_id)
        if success:
            await message.reply_text(f"✅ **New admin added:** `{user_id}`")
        else:
            await message.reply_text("⚠️ **This user is already an admin!**")
    except ValueError:
        await message.reply_text("❌ User ID must be a number!")

@Client.on_message(filters.command("del_admin") & filters.private)
async def remove_admin_user(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return await message.reply_text("⚠️ **Warning:** You are not the bot owner! Only the owner can remove admins.")

    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/del_admin UserID`")
        
    try:
        user_id = int(message.command[1])
        await db.remove_admin(user_id)
        await message.reply_text(f"🗑 **Admin removed:** `{user_id}`")
    except ValueError:
        await message.reply_text("❌ User ID must be a number!")

@Client.on_message(filters.command("mode") & filters.private)
async def toggle_bot_mode(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return await message.reply_text("⚠️ **Warning:** You are not the bot owner! Only the owner can change the public/private mode.")

    if len(message.command) < 2 or message.command[1].lower() not in ['public', 'private']:
        return await message.reply_text("❌ **Usage:** `/mode public` or `/mode private`")
        
    new_mode = message.command[1].lower()
    await db.update_settings('mode', new_mode)
    
    if new_mode == 'private':
        await message.reply_text("🔒 **Bot is now PRIVATE!**\nRegular users can no longer get any files.")
    else:
        await message.reply_text("🔓 **Bot is now PUBLIC!**\nEveryone can get files from the bot.")

@Client.on_message(filters.command("add_fsub") & filters.private)
async def add_fsub_channel(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return await message.reply_text(Script.NOT_OWNER_WARN)
        
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/add_fsub -100xxxxxxx`")
        
    try:
        chat_id = int(message.command[1])
        fsubs = await db.get_fsub_channels()
        if len(fsubs) >= 6:
            return await message.reply_text("❌ **You can add a maximum of 6 FSub channels!**")
            
        await db.add_fsub_channel(chat_id)
        await message.reply_text(f"✅ **Force Subscribe Channel Added:** `{chat_id}`")
    except ValueError:
        await message.reply_text("❌ Channel ID must be a number!")

@Client.on_message(filters.command("del_fsub") & filters.private)
async def remove_fsub_channel(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return await message.reply_text(Script.NOT_OWNER_WARN)
        
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/del_fsub -100xxxxxxx`")
        
    try:
        chat_id = int(message.command[1])
        await db.remove_fsub_channel(chat_id)
        await message.reply_text(f"🗑 **Force Subscribe Channel Removed:** `{chat_id}`")
    except ValueError:
        await message.reply_text("❌ Channel ID must be a number!")

@Client.on_message(filters.command("fsub_list") & filters.private)
async def list_fsub_channels(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID: return
    
    fsubs = await db.get_fsub_channels()
    if not fsubs:
        return await message.reply_text("⚠️ **No FSub channels are set!**")
        
    text = "📌 **Your current FSub channels:**\n\n"
    for idx, chat_id in enumerate(fsubs, start=1):
        text += f"{idx}. `{chat_id}`\n"
    await message.reply_text(text)

@Client.on_message(filters.command("req_fsub") & filters.private)
async def toggle_req_fsub(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return await message.reply_text(Script.NOT_OWNER_WARN)

    if len(message.command) < 2 or message.command[1].lower() not in ['on', 'off']:
        return await message.reply_text("❌ **Usage:** `/req_fsub on` or `/req_fsub off`")
        
    status = True if message.command[1].lower() == 'on' else False
    await db.update_settings('req_fsub', status)
    
    if status:
        await message.reply_text("✅ **Request to Join (Admin Approval) is now ON!**\nUsers must send a join request.")
    else:
        await message.reply_text("❌ **Request to Join is now OFF!**\nUsers can join directly.")

# 🚀 SECURE UPDATE: /set_delete command properly configured with script.py
@Client.on_message(filters.command(["auto_delete", "set_delete"]) & filters.private)
async def toggle_auto_delete(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return await message.reply_text(Script.NOT_OWNER_WARN)

    if len(message.command) < 2:
        return await message.reply_text(Script.SET_DELETE_USAGE)
        
    arg = message.command[1].lower()
    if arg == 'off':
        await db.update_settings('auto_delete', 0)
        await message.reply_text(Script.SET_DELETE_OFF)
    elif arg.isdigit():
        mins = int(arg)
        await db.update_settings('auto_delete', mins)
        await message.reply_text(Script.SET_DELETE_ON.format(mins=mins))
    else:
        await message.reply_text(Script.SET_DELETE_USAGE)
