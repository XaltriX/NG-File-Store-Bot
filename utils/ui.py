import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageNotModified
from config import Config
from utils.database import db
from utils.helpers import ist_date, ist_str, trial_info, clean_url
from utils.i18n import tr

NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def kb(rows):
    return InlineKeyboardMarkup(rows)


def btn(text, data=None, url=None):
    if url:
        return InlineKeyboardButton(text, url=url)
    return InlineKeyboardButton(text, callback_data=data)


async def show(client, query, text, markup=None, fresh=False):
    """Edit the callback message in place (caption or text). Falls back to a fresh message."""
    m = query.message
    if not fresh:
        try:
            if m.photo or m.video or m.document:
                if len(text) > 1000:
                    raise ValueError("caption too long")
                await m.edit_caption(text, reply_markup=markup, parse_mode=ParseMode.HTML)
            else:
                await m.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML,
                                  link_preview_options=NO_PREVIEW)
            return
        except MessageNotModified:
            return
        except Exception:
            pass
    try:
        await m.delete()
    except Exception:
        pass
    await client.send_message(m.chat.id, text, reply_markup=markup, parse_mode=ParseMode.HTML,
                              link_preview_options=NO_PREVIEW)


async def edit_by_id(client, chat_id, msg_id, text, markup=None):
    """Edit a stored message (used after admin text input)."""
    try:
        await client.edit_message_text(chat_id, msg_id, text, reply_markup=markup,
                                       parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW)
    except MessageNotModified:
        pass
    except Exception:
        try:
            await client.edit_message_caption(chat_id, msg_id, text, reply_markup=markup, parse_mode=ParseMode.HTML)
        except Exception:
            await client.send_message(chat_id, text, reply_markup=markup, parse_mode=ParseMode.HTML,
                                      link_preview_options=NO_PREVIEW)


def more_row(settings, lang):
    """Full-width 'More Videos' button (the Preview link). [] when no link is set."""
    url = clean_url((settings or {}).get('preview_link', ''))
    return [[btn(tr(lang, 'b_more'), url=url)]] if url else []


async def welcome_view(user_id, mention, user, settings, is_admin):
    lang = (user or {}).get('lang') or 'en'
    text = tr(lang, 'welcome', name=mention)

    exp = await db.premium_expire(user_id)
    if exp:
        text += tr(lang, 'w_premium', date=ist_str(exp))
    else:
        info = trial_info(user or {}, settings)
        if settings.get('shortlink_status') and not is_admin:
            if info['phase'] == 'active':
                text += tr(lang, 'w_trial', day=info['day'], days=info['days'], left=info['left'], daily=info['daily'])
            elif info['phase'] == 'new':
                text += tr(lang, 'w_trial_new', days=info['days'], daily=info['daily'])
            elif settings.get('shortlink_type') == 'credit':
                text += tr(lang, 'w_credits', creds=(user or {}).get('credits', 0))

    rows = [[btn(tr(lang, 'b_status'), 'u:status'), btn(tr(lang, 'b_premium'), 'prem_open')]]
    if settings.get('ref_enabled', True):
        rows.append([btn(tr(lang, 'b_refer'), 'u:refer')])
    row2 = []
    if clean_url(Config.UPDATES_LINK):
        row2.append(btn(tr(lang, 'b_updates'), url=clean_url(Config.UPDATES_LINK)))
    if clean_url(Config.SUPPORT_LINK):
        row2.append(btn(tr(lang, 'b_support'), url=clean_url(Config.SUPPORT_LINK)))
    if row2:
        rows.append(row2)
    if is_admin:
        rows.append([btn(tr('en', 'b_admin'), 'ap:home')])
    rows.extend(more_row(settings, lang))
    return text, kb(rows)


async def status_view(user_id, user, settings, is_admin):
    lang = (user or {}).get('lang') or 'en'
    user = user or {}

    exp = await db.premium_expire(user_id)
    plan = tr(lang, 'st_prem', date=ist_str(exp)) if exp else tr(lang, 'st_free')

    info = trial_info(user, settings)
    ph = info['phase']
    if ph == 'active':
        trial = tr(lang, 'st_trial_on', day=info['day'], days=info['days'], left=info['left'], daily=info['daily'])
    elif ph == 'new':
        trial = tr(lang, 'st_trial_new')
    elif ph == 'ended':
        trial = tr(lang, 'st_trial_end')
    else:
        trial = tr(lang, 'st_trial_off')

    if not settings.get('shortlink_status'):
        access = tr(lang, 'st_acc_open')
    elif settings.get('shortlink_type') == 'credit':
        access = tr(lang, 'st_acc_credit', creds=user.get('credits', 0))
    else:
        vexp = await db.verified_expire(user_id)
        access = tr(lang, 'st_acc_time', time=ist_str(vexp, '%d %b, %I:%M %p')) if vexp else tr(lang, 'st_acc_none')

    limit = int(settings.get('free_daily_limit', 0) or 0)
    used = user.get('free_used_today', 0) if user.get('free_last_date') == ist_date() else 0
    free = tr(lang, 'st_free_left', left=max(limit - used, 0), limit=limit)

    text = tr(lang, 'status', plan=plan, trial=trial, access=access, free=free)
    rows = [[btn(tr(lang, 'b_premium'), 'prem_open'), btn(tr(lang, 'b_lang'), 'u:lang')],
            [btn(tr(lang, 'b_back'), 'u:home')]]
    return text, kb(rows)
