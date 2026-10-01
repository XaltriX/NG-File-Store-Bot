import html
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from config import Config
from utils.database import db
from utils.helpers import clean_url, ist_str
from utils.i18n import tr, PREMIUM_CARD_EN, PREMIUM_CARD_HI
from utils.ui import btn, kb, show


# ================= Helpers =================
def plan_name(plan, lang):
    if lang == 'hi' and plan.get('name_hi'):
        return plan['name_hi']
    return plan['name']


def plan_label(plan, lang='en'):
    return f"₹{plan['price']} · {plan_name(plan, lang)}"


def find_plan(settings, plan_id):
    for p in settings.get('premium_plans', []):
        if p.get('id') == plan_id:
            return p
    return None


def owner_url(settings):
    handle = (settings.get('owner_handle') or '').strip().lstrip('@')
    return f"https://t.me/{handle}" if handle else clean_url(Config.SUPPORT_LINK)


def render_card(settings, lang):
    tpl = settings.get('premium_card_hi' if lang == 'hi' else 'premium_card')
    if not tpl:
        tpl = PREMIUM_CARD_HI if lang == 'hi' else PREMIUM_CARD_EN
    plans = "\n".join(f"🪙 ₹{p['price']} — {html.escape(plan_name(p, lang))}" for p in settings.get('premium_plans', []))
    return (tpl.replace('{plans}', plans)
               .replace('{upi}', html.escape(settings.get('upi_id', '')))
               .replace('{owner}', html.escape(settings.get('owner_handle', ''))))


def plans_view(settings, lang):
    plans = settings.get('premium_plans', [])
    if not plans:
        return tr(lang, 'prem_gone'), kb([[btn(tr(lang, 'b_back'), 'u:home')]])
    rows, row = [], []
    for p in plans:
        row.append(btn('🪙 ' + plan_label(p, lang), f"prem_plan:{p['id']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    links = []
    for key, label in (('info_link', '📋 Info'), ('preview_link', '👀 Preview'),
                       ('proofs_link', '⭐ Proofs'), ('qr_link', '📱 QR')):
        url = clean_url(settings.get(key, ''))
        if url:
            links.append(btn(label, url=url))
    if links:
        rows.append(links)
    rows.append([btn(tr(lang, 'b_back'), 'u:home')])
    return render_card(settings, lang), kb(rows)


async def user_lang(user_id):
    user = await db.get_user(user_id)
    return (user or {}).get('lang') or 'en'


# ================= User flow =================
@Client.on_callback_query(filters.regex(r"^prem_(open|back)$"))
async def prem_open_cb(client: Client, query: CallbackQuery):
    settings = await db.get_settings()
    lang = await user_lang(query.from_user.id)
    text, markup = plans_view(settings, lang)
    await show(client, query, text, markup, fresh=(query.data == "prem_back"))
    await query.answer()


@Client.on_message(filters.command(["plan", "premium", "buy"]) & filters.private)
async def plan_command(client: Client, message: Message):
    settings = await db.get_settings()
    lang = await user_lang(message.from_user.id)
    text, markup = plans_view(settings, lang)
    await message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^prem_plan:"))
async def prem_plan_cb(client: Client, query: CallbackQuery):
    settings = await db.get_settings()
    lang = await user_lang(query.from_user.id)
    plan = find_plan(settings, query.data.split(":")[1])
    if not plan:
        return await query.answer(tr(lang, 'prem_gone'), show_alert=True)

    caption = tr(lang, 'pay_caption', plan=html.escape(plan_label(plan, lang)), upi=html.escape(settings.get('upi_id', '')))
    markup = kb([[btn(tr(lang, 'b_paid'), f"prem_paid:{plan['id']}"), btn(tr(lang, 'b_change'), 'prem_back')]])
    chat_id = query.message.chat.id
    try:
        await query.message.delete()
    except Exception:
        pass

    qr_url = clean_url(settings.get('qr_url', ''))
    cached = settings.get('qr_file_id')
    sent = None
    for source in (cached, qr_url):
        if not source:
            continue
        try:
            sent = await client.send_photo(chat_id, source, caption=caption, reply_markup=markup, parse_mode=ParseMode.HTML)
            if source == qr_url and sent.photo:
                await db.update_settings('qr_file_id', sent.photo.file_id)
            break
        except Exception:
            continue
    if not sent:
        await client.send_message(chat_id, caption, reply_markup=markup, parse_mode=ParseMode.HTML)
    await query.answer()


@Client.on_callback_query(filters.regex(r"^prem_paid:"))
async def prem_paid_cb(client: Client, query: CallbackQuery):
    settings = await db.get_settings()
    user_id = query.from_user.id
    lang = await user_lang(user_id)
    plan = find_plan(settings, query.data.split(":")[1])
    if not plan:
        return await query.answer(tr(lang, 'prem_gone'), show_alert=True)
    if await db.pending_payment(user_id):
        return await query.answer(tr(lang, 'ss_pending'), show_alert=True)

    await db.set_pay_plan(user_id, plan['id'])
    text = tr(lang, 'ask_ss', plan=html.escape(plan_label(plan, lang)))
    markup = kb([[btn(tr(lang, 'b_cancel'), 'prem_cancel')]])
    try:
        await query.message.edit_caption(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception:
        await client.send_message(query.message.chat.id, text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await query.answer()


@Client.on_callback_query(filters.regex(r"^prem_cancel$"))
async def prem_cancel_cb(client: Client, query: CallbackQuery):
    await db.set_pay_plan(query.from_user.id, None)
    settings = await db.get_settings()
    lang = await user_lang(query.from_user.id)
    text, markup = plans_view(settings, lang)
    await show(client, query, text, markup, fresh=True)
    await query.answer()


@Client.on_message(filters.private & (filters.photo | filters.document), group=-2)
async def screenshot_handler(client: Client, message: Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    plan_id = (user or {}).get('pay_plan')
    if not plan_id or await db.is_admin(user_id):
        return  # not a payment screenshot, let other handlers run

    lang = (user or {}).get('lang') or 'en'
    is_image = bool(message.photo) or (message.document and (message.document.mime_type or '').startswith('image/'))
    if not is_image:
        await message.reply_text(tr(lang, 'ss_bad'))
        message.stop_propagation()

    settings = await db.get_settings()
    plan = find_plan(settings, plan_id)
    if not plan:
        await db.set_pay_plan(user_id, None)
        return
    if await db.pending_payment(user_id):
        await db.set_pay_plan(user_id, None)
        await message.reply_text(tr(lang, 'ss_pending'))
        message.stop_propagation()

    pay_id = await db.create_payment(user_id, plan)
    caption = (
        "💳 <b>NEW PAYMENT REQUEST</b>\n\n"
        f"👤 {message.from_user.mention} · <code>{user_id}</code>\n"
        f"📦 Selected: <b>{html.escape(plan_label(plan))}</b>\n\n"
        "<i>Check the screenshot, then approve the amount actually paid.</i>"
    )
    rows = [[InlineKeyboardButton(f"✅ Approve {plan_label(plan)}", callback_data=f"payok:{pay_id}:{plan['id']}")]]
    others, row = [p for p in settings.get('premium_plans', []) if p['id'] != plan['id']], []
    for p in others:
        row.append(InlineKeyboardButton(plan_label(p), callback_data=f"payok:{pay_id}:{p['id']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("❌ Reject", callback_data=f"payno:{pay_id}")])

    try:
        await message.copy(Config.OWNER_ID, caption=caption, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
    except Exception:
        await message.reply_text(tr(lang, 'rejected'))
        message.stop_propagation()

    await db.set_pay_plan(user_id, None)
    await message.reply_text(tr(lang, 'ss_got'), parse_mode=ParseMode.HTML)
    message.stop_propagation()


# ================= Admin approval =================
@Client.on_callback_query(filters.regex(r"^payok:"))
async def pay_ok_cb(client: Client, query: CallbackQuery):
    if not await db.is_admin(query.from_user.id):
        return await query.answer()
    _, pay_id, plan_id = query.data.split(":")
    settings = await db.get_settings()
    plan = find_plan(settings, plan_id)
    if not plan:
        return await query.answer("Plan not found.", show_alert=True)
    pay = await db.claim_payment(pay_id, 'approved', query.from_user.id, plan_id)
    if not pay:
        return await query.answer("Already handled.", show_alert=True)

    buyer = pay['u']
    expire_at = await db.extend_premium(buyer, plan['days'])
    await db.bump_stat('prem_approved')
    lang = await user_lang(buyer)
    selected = find_plan(settings, pay['plan'])

    markup = None
    if selected and selected['id'] != plan['id']:
        text = tr(lang, 'approved_diff', sel=html.escape(plan_label(selected, lang)),
                  plan=html.escape(plan_label(plan, lang)), date=ist_str(expire_at))
        markup = kb([[btn(tr(lang, 'b_upgrade'), 'prem_back')]])
    else:
        text = tr(lang, 'approved', plan=html.escape(plan_label(plan, lang)), date=ist_str(expire_at))
    try:
        await client.send_message(buyer, text, reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception:
        pass

    old = query.message.caption.html if query.message.caption else ""
    try:
        await query.message.edit_caption(f"{old}\n\n✅ <b>Approved:</b> {html.escape(plan_label(plan))} · till {ist_str(expire_at)}",
                                         parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await query.answer("Premium activated.")


@Client.on_callback_query(filters.regex(r"^payno:"))
async def pay_no_cb(client: Client, query: CallbackQuery):
    if not await db.is_admin(query.from_user.id):
        return await query.answer()
    pay_id = query.data.split(":")[1]
    pay = await db.claim_payment(pay_id, 'rejected', query.from_user.id)
    if not pay:
        return await query.answer("Already handled.", show_alert=True)

    settings = await db.get_settings()
    lang = await user_lang(pay['u'])
    markup = kb([[btn(tr(lang, 'b_contact'), url=owner_url(settings))]])
    try:
        await client.send_message(pay['u'], tr(lang, 'rejected'), reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    old = query.message.caption.html if query.message.caption else ""
    try:
        await query.message.edit_caption(f"{old}\n\n❌ <b>Rejected</b>", parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await query.answer("Rejected.")


# ================= Hidden shortcuts (panel does all of this too) =================
@Client.on_message(filters.command("set_free_limit") & filters.private)
async def set_free_limit_cmd(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/set_free_limit 3` (0 to disable)")
    try:
        limit = int(message.command[1])
        await db.update_settings('free_daily_limit', limit)
        await message.reply_text(f"✅ Daily free limit set to: {limit}")
    except ValueError:
        await message.reply_text("❌ Limit must be a number!")


@Client.on_message(filters.command("add_prem") & filters.private)
async def add_premium_cmd(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return
    parts = message.command
    if len(parts) < 3:
        return await message.reply_text("Usage: <code>/add_prem user_id days</code>", parse_mode=ParseMode.HTML)
    try:
        user_id, days = int(parts[1]), int(parts[2])
        expire_at = await db.extend_premium(user_id, days)
        await message.reply_text(f"✅ Premium added for <code>{user_id}</code> · till {ist_str(expire_at)}", parse_mode=ParseMode.HTML)
        lang = await user_lang(user_id)
        try:
            await client.send_message(user_id, tr(lang, 'approved', plan=f"{days} days", date=ist_str(expire_at)), parse_mode=ParseMode.HTML)
        except Exception:
            pass
    except ValueError:
        await message.reply_text("❌ ID and days must be numbers!")


@Client.on_message(filters.command("del_prem") & filters.private)
async def del_premium_cmd(client: Client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        return
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code>/del_prem user_id</code>", parse_mode=ParseMode.HTML)
    try:
        await db.remove_premium(int(message.command[1]))
        await message.reply_text("🗑 Premium removed.")
    except ValueError:
        pass
