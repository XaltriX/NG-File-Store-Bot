import time
import asyncio
import random
import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, LinkPreviewOptions
from pyrogram.errors import FloodWait, ChannelInvalid, ChannelPrivate, ChatAdminRequired
from pyrogram.enums import ParseMode
from config import Config
from utils.database import db
from utils.fsub_helper import check_fsub, get_fsub_keyboard
from utils.shortener import get_shortlink
from utils.shortlink_guard import ShortlinkGuard
from script import Script
from utils.i18n import tr
from utils.ui import welcome_view, status_view, show

FILE_CACHE = {}
MAX_CACHE_SIZE = 50

# 🚀 ANTI-SPAM CACHE FOR FILE DELIVERY 
DELIVERY_CACHE = {}
DELIVERY_CACHE_TTL = 3

# 🚀 SMART LEGACY DECODER
OLD_DB_CHANNEL = Config.OLD_DB_CHANNEL or Config.DB_CHANNEL

# 🚀 SMART ID FORMATTER (Bulletproof Fix)
def get_correct_chat_id(chat_id):
    if not chat_id: return chat_id
    try:
        chat_id_str = str(chat_id).strip()
        if chat_id_str.startswith("-100"): return int(chat_id_str)
        if chat_id_str.startswith("-"): return int(f"-100{chat_id_str[1:]}")
        return int(f"-100{chat_id_str}")
    except Exception: return chat_id

async def decode_legacy_link(payload: str):
    try:
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding).decode('utf-8')
        parts = decoded.split("-")
        db_abs = abs(OLD_DB_CHANNEL)
        
        if len(parts) == 3:
            return {'t': 'b', 'c': OLD_DB_CHANNEL, 'f_id': int(int(parts[1]) / db_abs), 'l_id': int(int(parts[2]) / db_abs)}
        elif len(parts) == 2:
            return {'t': 's', 'c': OLD_DB_CHANNEL, 'm': int(int(parts[1]) / db_abs)}
        elif len(parts) == 5:
            return {'t': 'b', 'c': OLD_DB_CHANNEL, 'f_id': int(int(parts[3]) / db_abs), 'l_id': int(int(parts[4]) / db_abs)}
        elif len(parts) == 4:
            return {'t': 's', 'c': OLD_DB_CHANNEL, 'm': int(int(parts[3]) / db_abs)}
    except Exception:
        return None

async def get_cached_file(unique_id: str):
    if unique_id in FILE_CACHE:
        val = FILE_CACHE.pop(unique_id)
        FILE_CACHE[unique_id] = val
        return val
    file_data = await db.get_file(unique_id)
    if not file_data:
        file_data = await decode_legacy_link(unique_id)
    if file_data:
        FILE_CACHE[unique_id] = file_data
        if len(FILE_CACHE) > MAX_CACHE_SIZE:
            FILE_CACHE.pop(next(iter(FILE_CACHE)))
    return file_data

def clean_url(url: str) -> str:
    if not url: return ""
    url = url.strip("<>[]()\"' ")
    if not url: return ""
    if url.startswith("t.me/"): return "https://" + url
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("tg://")):
        return "https://" + url
    return url

def format_caption(original_caption: str) -> str:
    if original_caption:
        return f"{original_caption}{Script.BRANDING_TAG}"
    return Script.BRANDING_TAG.strip()

async def delete_after_delay(client, chat_id, message_ids, delay):
    await asyncio.sleep(delay)
    warn_msg_id = message_ids[-1]
    file_msg_ids = message_ids[:-1]
    
    try:
        if file_msg_ids:
            await client.delete_messages(chat_id, file_msg_ids)
    except Exception:
        pass
        
    try:
        await client.edit_message_text(chat_id, warn_msg_id, Script.AUTO_DELETE_DONE)
    except Exception:
        pass

async def deliver_file(client: Client, chat_id: int, payload: str, reply_to_msg=None):
    unique_id = payload
        
    try:
        file_data = await get_cached_file(unique_id)
        if not file_data:
            if reply_to_msg:
                await reply_to_msg.reply_text(Script.INVALID_LINK)
            else:
                await client.send_message(chat_id, Script.INVALID_LINK)
            return

        sent_msg_ids = []
        settings = await db.get_settings()
        auto_delete_time = settings.get('auto_delete', 0)
        is_protected = settings.get('protect_content', False)

        if file_data.get('t') == 'b':
            if 'files' in file_data:
                # 🚀 PURE PERMANENT BATCH MODE (No Channel Needed)
                total_files = len(file_data['files'])
                wait_text = Script.BATCH_SENDING.format(total_files=total_files)
                wait_msg = await reply_to_msg.reply_text(wait_text) if reply_to_msg else await client.send_message(chat_id, wait_text)
                
                success_sent = 0
                needs_db_update = False 
                for f_item in file_data['files']:
                    try:
                        final_cap = format_caption(f_item.get('cap', ''))
                        sent_m = None
                        if 'f' in f_item:
                            sent_m = await client.send_cached_media(chat_id, f_item['f'], caption=final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                        else:
                            sent_m = await client.send_message(chat_id, final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                        if sent_m: 
                            sent_msg_ids.append(sent_m.id)
                            success_sent += 1
                    except Exception:
                        # 🚀 SMART HYBRID AUTO-HEALING FALLBACK (BATCH)
                        try:
                            if 'c' in file_data and 'm' in f_item:
                                real_c_id = get_correct_chat_id(file_data['c']) 
                                db_msg = await client.get_messages(real_c_id, f_item['m'])
                                if db_msg and not getattr(db_msg, "empty", True):
                                    if db_msg.media: 
                                        sent_m = await client.copy_message(chat_id, real_c_id, f_item['m'], caption=final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                                        media = db_msg.document or db_msg.video or db_msg.audio or db_msg.photo or db_msg.animation or db_msg.sticker or db_msg.voice
                                        if media:
                                            f_item['f'] = media.file_id if not isinstance(media, list) else media[-1].file_id
                                            needs_db_update = True
                                    else: 
                                        sent_m = await client.copy_message(chat_id, real_c_id, f_item['m'], protect_content=is_protected)
                                    if sent_m: 
                                        sent_msg_ids.append(sent_m.id)
                                        success_sent += 1
                        except Exception: pass
                    await asyncio.sleep(random.uniform(0.6, 1.8))
                    
                if needs_db_update: 
                    # 🚀 FIX: Multi-DB Auto-heal Support
                    try: await db.update_file_data(unique_id, {'files': file_data['files']})
                    except Exception: pass
                    
                try: await wait_msg.delete()
                except Exception: pass
                
                if success_sent == 0:
                    if reply_to_msg: await reply_to_msg.reply_text(Script.MSG_NOT_FOUND_SERVER)
                    else: await client.send_message(chat_id, Script.MSG_NOT_FOUND_SERVER)
                    return
                
                if auto_delete_time > 0:
                    success_msg = await client.send_message(chat_id, Script.BATCH_SUCCESS_WARN.format(auto_delete_time=auto_delete_time))
                    sent_msg_ids.append(success_msg.id)
                else: await client.send_message(chat_id, Script.BATCH_SUCCESS)
                
            else:
                # NORMAL BATCH MODE (Legacy)
                db_chat_id = get_correct_chat_id(file_data['c']) 
                first_id, last_id = file_data['f_id'], file_data['l_id']
                total_files = (last_id - first_id) + 1
                wait_text = Script.BATCH_SENDING.format(total_files=total_files)
                wait_msg = await reply_to_msg.reply_text(wait_text) if reply_to_msg else await client.send_message(chat_id, wait_text)
                
                success_sent = 0
                for msg_id in range(first_id, last_id + 1):
                    sent_m = None
                    try:
                        db_msg = await client.get_messages(db_chat_id, msg_id)
                        if db_msg and not getattr(db_msg, "empty", True):
                            final_cap = format_caption(db_msg.caption.html if db_msg.caption else (db_msg.text.html if db_msg.text else ""))
                            if db_msg.media:
                                sent_m = await client.copy_message(chat_id, db_chat_id, msg_id, caption=final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                            else:
                                sent_m = await client.copy_message(chat_id, db_chat_id, msg_id, protect_content=is_protected)
                        if sent_m: 
                            sent_msg_ids.append(sent_m.id)
                            success_sent += 1
                        await asyncio.sleep(random.uniform(0.6, 1.8)) 
                    except FloodWait as e:
                        await asyncio.sleep(e.value + random.uniform(1.0, 2.5))
                        sent_m = await client.copy_message(chat_id, db_chat_id, msg_id, protect_content=is_protected)
                        if sent_m: 
                            sent_msg_ids.append(sent_m.id)
                            success_sent += 1
                    except Exception: pass
                    
                try: await wait_msg.delete()
                except Exception: pass
                
                if success_sent == 0:
                    if reply_to_msg: await reply_to_msg.reply_text(Script.MSG_NOT_FOUND_SERVER)
                    else: await client.send_message(chat_id, Script.MSG_NOT_FOUND_SERVER)
                    return
                
                if auto_delete_time > 0:
                    success_msg = await client.send_message(chat_id, Script.BATCH_SUCCESS_WARN.format(auto_delete_time=auto_delete_time))
                    sent_msg_ids.append(success_msg.id)
                else: await client.send_message(chat_id, Script.BATCH_SUCCESS)
                
        else:
            if 'f' in file_data:
                # 🚀 PURE PERMANENT SINGLE MODE
                try:
                    final_cap = format_caption(file_data.get('cap', ''))
                    sent_m = await client.send_cached_media(chat_id, file_data['f'], caption=final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                except Exception:
                    # 🚀 SMART HYBRID AUTO-HEALING FALLBACK (SINGLE)
                    try:
                        if 'c' in file_data and 'm' in file_data:
                            real_c_id = get_correct_chat_id(file_data['c']) 
                            db_msg = await client.get_messages(real_c_id, file_data['m'])
                            if db_msg and not getattr(db_msg, "empty", True):
                                if db_msg.media: 
                                    sent_m = await client.copy_message(chat_id, real_c_id, file_data['m'], caption=final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                                    media = db_msg.document or db_msg.video or db_msg.audio or db_msg.photo or db_msg.animation or db_msg.sticker or db_msg.voice
                                    if media:
                                        new_f_id = media.file_id if not isinstance(media, list) else media[-1].file_id
                                        # 🚀 FIX: Multi-DB Auto-heal Support
                                        try: await db.update_file_data(unique_id, {'f': new_f_id})
                                        except Exception: pass
                                else: 
                                    sent_m = await client.copy_message(chat_id, real_c_id, file_data['m'], protect_content=is_protected)
                        else:
                            sent_m = await client.send_message(chat_id, Script.FILE_NOT_FOUND_SERVER)
                    except Exception:
                        sent_m = await client.send_message(chat_id, Script.FILE_NOT_FOUND_SERVER)
            elif 'c' not in file_data and 'cap' in file_data:
                try:
                    final_cap = format_caption(file_data.get('cap', ''))
                    sent_m = await client.send_message(chat_id, final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                except Exception:
                    sent_m = await client.send_message(chat_id, Script.FILE_NOT_FOUND_SERVER)
            else:
                # NORMAL SINGLE MODE
                db_chat_id = get_correct_chat_id(file_data['c']) 
                msg_id = file_data['m']
                sent_m = None
                try:
                    db_msg = await client.get_messages(db_chat_id, msg_id)
                    if db_msg and not getattr(db_msg, "empty", True):
                        final_cap = format_caption(db_msg.caption.html if db_msg.caption else (db_msg.text.html if db_msg.text else ""))
                        if db_msg.media:
                            sent_m = await client.copy_message(chat_id, db_chat_id, msg_id, caption=final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                        else:
                            sent_m = await client.copy_message(chat_id, db_chat_id, msg_id, protect_content=is_protected)
                    else: raise Exception("Empty")
                except (ChannelInvalid, ChannelPrivate, ChatAdminRequired, Exception):
                    if 'f' in file_data:
                        orig_cap = file_data.get('cap', '')
                        final_cap = format_caption(orig_cap)
                        try:
                            sent_m = await client.send_cached_media(chat_id, file_data['f'], caption=final_cap, parse_mode=ParseMode.HTML, protect_content=is_protected)
                        except Exception:
                            sent_m = await client.send_message(chat_id, Script.FILE_NOT_FOUND_SERVER)
                    elif 'cap' in file_data:
                        try: sent_m = await client.send_message(chat_id, format_caption(file_data.get('cap', '')), parse_mode=ParseMode.HTML, protect_content=is_protected)
                        except Exception: sent_m = await client.send_message(chat_id, Script.FILE_NOT_FOUND_SERVER)
                    else:
                        sent_m = await client.send_message(chat_id, Script.MSG_NOT_FOUND_SERVER)
            
            if sent_m and hasattr(sent_m, "id"): 
                sent_msg_ids.append(sent_m.id)
                if auto_delete_time > 0:
                    warn_msg = await client.send_message(chat_id, Script.SINGLE_SUCCESS_WARN.format(auto_delete_time=auto_delete_time))
                    sent_msg_ids.append(warn_msg.id)

        if auto_delete_time > 0 and sent_msg_ids:
            asyncio.create_task(delete_after_delay(client, chat_id, sent_msg_ids, auto_delete_time * 60))
            
    except Exception as e:
        await client.send_message(chat_id, Script.DELIVERY_ERROR)
    finally:
        pass


def bot_username_of(client):
    return client.me.username if client.me else None


async def send_verify_screen(client: Client, chat_id: int, user_id: int, payload: str, settings: dict, lang: str, phase: str = None):
    sl_n = await db.pick_shortner(user_id, settings)
    sl_url, sl_api, tutorial = db.sl_config(settings, sl_n)
    token = await db.create_verify_token(user_id, payload or '', sl_n)
    bot_username = bot_username_of(client) or (await client.get_me()).username

    wait_msg = await client.send_message(chat_id, tr(lang, 'generating'))

    short_url = None
    if settings.get('web_guard', False) and Config.GUARD_URL and Config.GUARD_SECRET:
        short_url = ShortlinkGuard.generate_cf_url(
            token=token, api_url=sl_url, api_key=sl_api,
            bot_username=bot_username, bypass_time=settings.get('bypass_time', 15)
        )
    if not short_url:
        verify_url = f"https://t.me/{bot_username}?start=verify_{token}"
        short_url = clean_url(await get_shortlink(verify_url, sl_url, sl_api))

    if settings.get('shortlink_type', 'time') == 'credit':
        benefit = tr(lang, 'benefit_credit', creds=settings.get('bypass_credits', 3))
    else:
        benefit = tr(lang, 'benefit_time', hours=settings.get('verify_duration', 24))

    if phase == 'ended':
        head_txt = tr(lang, 'locked_trial_end')
    elif phase == 'active':
        head_txt = tr(lang, 'locked_trial_today')
    else:
        head_txt = tr(lang, 'locked_normal')
    text = tr(lang, 'locked_body', head=head_txt, benefit=benefit)

    rows = []
    if short_url:
        rows.append([InlineKeyboardButton(tr(lang, 'b_verify'), url=short_url)])
    row2 = [InlineKeyboardButton(tr(lang, 'b_premium'), callback_data="prem_open")]
    tut = clean_url(tutorial)
    if tut:
        row2.append(InlineKeyboardButton(tr(lang, 'b_tutorial'), url=tut))
    rows.append(row2)
    markup = InlineKeyboardMarkup(rows)

    try: await wait_msg.delete()
    except Exception: pass

    verify_img = clean_url(Config.VERIFY_IMG)
    try:
        if verify_img:
            await client.send_photo(chat_id, verify_img, caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
        else:
            await client.send_message(chat_id, text, reply_markup=markup, parse_mode=ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))
    except Exception:
        await client.send_message(chat_id, text, reply_markup=markup, parse_mode=ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))


async def check_access(client: Client, chat_id: int, user_id: int, payload: str, settings: dict, user: dict):
    """Order: Admin > Premium > Trial > Free daily limit > Verify.
    Returns (locked, note)."""
    lang = (user or {}).get('lang') or 'en'
    if await db.is_admin(user_id) or await db.check_and_use_premium(user_id):
        return False, None

    info, phase = await db.use_trial(user_id, settings)
    if info:
        if info['left'] > 0:
            text = tr(lang, 'trial_note', day=info['day'], days=info['days'], left=info['left'], daily=info['daily'])
            return False, {'text': text, 'last': False}
        return False, {'text': tr(lang, 'trial_last'), 'last': True}

    free_limit = settings.get('free_daily_limit', 0)
    if free_limit > 0 and await db.check_and_use_free_limit(user_id, free_limit):
        return False, None

    sl_type = settings.get('shortlink_type', 'time')
    needs_verify = False
    if sl_type == 'time':
        if not await db.is_user_verified(user_id, int(time.time())):
            needs_verify = True
    elif sl_type == 'credit':
        if not await db.use_credit(user_id):
            needs_verify = True

    if needs_verify:
        await send_verify_screen(client, chat_id, user_id, payload, settings, lang, phase)
        return True, None
    return False, None


async def send_note(client: Client, chat_id: int, note: dict, lang: str):
    if not note:
        return
    markup = None
    if note.get('last'):
        bot_username = bot_username_of(client) or (await client.get_me()).username
        markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(tr(lang, 'b_verify'), url=f"https://t.me/{bot_username}?start=getverify"),
            InlineKeyboardButton(tr(lang, 'b_premium'), callback_data="prem_open"),
        ]])
    try:
        await client.send_message(chat_id, note['text'], reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception:
        pass


async def complete_verification(client: Client, message: Message, user_id: int, token_data: dict, settings: dict, lang: str):
    sl_n = token_data.get('sl', 1)
    if settings.get('shortlink_type', 'time') == 'time':
        duration = settings.get('verify_duration', 24)
        await db.verify_user(user_id, int(time.time()) + duration * 3600)
        text = tr(lang, 'ver_ok_time', duration=duration)
    else:
        creds = settings.get('bypass_credits', 3)
        await db.add_credits(user_id, creds)
        text = tr(lang, 'ver_ok_credit', creds=creds)

    await db.set_last_sl(user_id, sl_n)
    await db.log_verify(user_id, sl_n)

    payload = token_data.get('payload')
    if payload:
        success_msg = await message.reply_text(text, parse_mode=ParseMode.HTML)
        await asyncio.sleep(1.5)
        await deliver_file(client, message.chat.id, payload, reply_to_msg=success_msg)
    else:
        await db.bump_stat('reminder_verifies')
        await message.reply_text(text + tr(lang, 'ver_ok_nofile'), parse_mode=ParseMode.HTML)


async def send_welcome(client: Client, chat_id: int, user_id: int, mention: str, settings: dict, is_admin: bool, reply_to: int = None):
    user = await db.get_user(user_id)
    text, markup = await welcome_view(user_id, mention, user, settings, is_admin)
    start_pic = getattr(Config, "START_PIC", None)
    if start_pic:
        try:
            return await client.send_photo(chat_id, start_pic, caption=text, reply_markup=markup, parse_mode=ParseMode.HTML)
        except Exception:
            pass
    await client.send_message(chat_id, text, reply_markup=markup, parse_mode=ParseMode.HTML, link_preview_options=LinkPreviewOptions(is_disabled=True))


def language_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("English", callback_data="u:setlang:en"),
        InlineKeyboardButton("हिंदी", callback_data="u:setlang:hi"),
    ]])


@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    current_time = time.time()

    expired_keys = [k for k, v in DELIVERY_CACHE.items() if v <= current_time]
    for k in expired_keys:
        del DELIVERY_CACHE[k]

    if user_id in DELIVERY_CACHE and current_time < DELIVERY_CACHE[user_id]:
        return
    DELIVERY_CACHE[user_id] = current_time + DELIVERY_CACHE_TTL

    if await db.is_banned(user_id):
        support_btn = []
        if Config.SUPPORT_LINK:
            support_btn.append([InlineKeyboardButton(Script.BTN_CONTACT_SUPPORT, url=clean_url(Config.SUPPORT_LINK))])
        reply_markup = InlineKeyboardMarkup(support_btn) if support_btn else None
        return await message.reply_text(Script.BANNED_MSG, reply_markup=reply_markup)

    is_new_user = await db.add_user(user_id)
    settings = await db.get_settings()
    is_admin = await db.is_admin(user_id)
    user = await db.get_user(user_id) or {}
    lang = user.get('lang') or 'en'
    await db.reset_ignored(user_id)

    log_channel = settings.get('log_channel')
    if is_new_user and log_channel:
        try:
            await client.send_message(
                log_channel,
                Script.NEW_USER_LOG.format(mention=message.from_user.mention, user_id=user_id, text=message.text)
            )
        except Exception:
            pass

    if settings.get('mode') == 'private' and not is_admin:
        await message.reply_text(Script.PRIVATE_MODE_MSG)
        return

    text = message.text
    payload = text.split()[1] if len(text.split()) > 1 else None

    if not is_admin:
        missing_fsubs = await check_fsub(client, user_id)
        if missing_fsubs:
            keyboard = await get_fsub_keyboard(client, missing_fsubs, payload)
            await message.reply_text(Script.FSUB_WARNING, reply_markup=keyboard)
            return

    if payload:
        if payload.startswith("vpass_"):
            if not (Config.GUARD_URL and Config.GUARD_SECRET):
                return await message.reply_text(Script.VERIFY_INVALID)
            parts = payload.split("_")
            if len(parts) >= 3:
                token, signature = parts[1], parts[2]
                if signature == ShortlinkGuard.generate_signature(token):
                    token_data = await db.get_verify_token(token)
                    if token_data and token_data['user_id'] == user_id:
                        await complete_verification(client, message, user_id, token_data, settings, lang)
                    else:
                        return await message.reply_text(Script.VERIFY_INVALID)
                else:
                    return await message.reply_text(Script.GUARD_BANNED)
            else:
                return await message.reply_text(Script.VERIFY_INVALID)
            return

        elif payload.startswith("verify_"):
            token = payload.split("_")[1]
            token_data = await db.get_verify_token(token)
            if token_data and token_data['user_id'] == user_id:
                bypass_time = settings.get('bypass_time', 15)
                time_taken = int(time.time()) - token_data.get('createdAt', 0)
                if bypass_time > 0 and time_taken < bypass_time:
                    return await message.reply_text(Script.BYPASS_DETECTED)
                await complete_verification(client, message, user_id, token_data, settings, lang)
            else:
                await message.reply_text(Script.VERIFY_INVALID)
            return

        elif payload == "getverify":
            await db.bump_stat('reminder_clicks')
            active = (is_admin or await db.premium_expire(user_id) or not settings.get('shortlink_status'))
            if not active:
                if settings.get('shortlink_type', 'time') == 'credit':
                    active = (user.get('credits', 0) > 0)
                else:
                    active = bool(await db.verified_expire(user_id))
            if active:
                return await message.reply_text(tr(lang, 'already_active'))
            await send_verify_screen(client, message.chat.id, user_id, '', settings, lang)
            return

        note = None
        if settings.get('shortlink_status'):
            locked, note = await check_access(client, message.chat.id, user_id, payload, settings, user)
            if locked:
                return

        await deliver_file(client, message.chat.id, payload, reply_to_msg=message)
        await send_note(client, message.chat.id, note, lang)
        return

    if not user.get('lang'):
        return await message.reply_text(tr('en', 'lang_pick'), reply_markup=language_keyboard(), parse_mode=ParseMode.HTML)

    await send_welcome(client, message.chat.id, user_id, message.from_user.mention, settings, is_admin)


@Client.on_callback_query(filters.regex(r"^chkF_"))
async def check_fsub_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id

    if await db.is_banned(user_id):
        support_btn = []
        if Config.SUPPORT_LINK:
            support_btn.append([InlineKeyboardButton(Script.BTN_CONTACT_SUPPORT, url=clean_url(Config.SUPPORT_LINK))])
        reply_markup = InlineKeyboardMarkup(support_btn) if support_btn else None
        await query.message.reply_text(Script.BANNED_CB_MSG, reply_markup=reply_markup)
        return await query.answer(Script.BANNED_CB_ALERT, show_alert=True)

    payload = query.data.split("_", 1)[1]
    missing_fsubs = await check_fsub(client, user_id)

    if missing_fsubs:
        await query.answer(Script.FSUB_NOT_JOINED_ALERT, show_alert=True)
        return

    await query.answer(Script.FSUB_JOINED_ALERT, show_alert=True)
    chat_id = query.message.chat.id
    try:
        await query.message.delete()
    except Exception:
        pass

    settings = await db.get_settings()
    is_admin = await db.is_admin(user_id)
    if settings.get('mode') == 'private' and not is_admin:
        return await client.send_message(chat_id, Script.PRIVATE_MODE_MSG)

    user = await db.get_user(user_id) or {}
    lang = user.get('lang') or 'en'
    note = None
    if settings.get('shortlink_status'):
        locked, note = await check_access(client, chat_id, user_id, payload, settings, user)
        if locked:
            return

    await deliver_file(client, chat_id, payload)
    await send_note(client, chat_id, note, lang)


@Client.on_callback_query(filters.regex(r"^(u:|close_menu$|close_data$)"))
async def user_menu_callbacks(client: Client, query: CallbackQuery):
    action = query.data
    user_id = query.from_user.id

    if action in ("close_menu", "close_data"):
        try: await query.message.delete()
        except Exception: pass
        return await query.answer()

    settings = await db.get_settings()
    is_admin = await db.is_admin(user_id)
    user = await db.get_user(user_id) or {}
    lang = user.get('lang') or 'en'

    if action == "u:home":
        text, markup = await welcome_view(user_id, query.from_user.mention, user, settings, is_admin)
        await show(client, query, text, markup)

    elif action == "u:status":
        text, markup = await status_view(user_id, user, settings, is_admin)
        await show(client, query, text, markup)

    elif action == "u:lang":
        await show(client, query, tr('en', 'lang_pick'), language_keyboard())

    elif action.startswith("u:setlang:"):
        new_lang = action.split(":")[2]
        if new_lang in ("en", "hi"):
            await db.set_lang(user_id, new_lang)
            user['lang'] = new_lang
        text, markup = await welcome_view(user_id, query.from_user.mention, user, settings, is_admin)
        start_pic = getattr(Config, "START_PIC", None)
        if query.message.photo or not start_pic:
            await show(client, query, text, markup)
        else:
            try: await query.message.delete()
            except Exception: pass
            await send_welcome(client, query.message.chat.id, user_id, query.from_user.mention, settings, is_admin)

    await query.answer()
