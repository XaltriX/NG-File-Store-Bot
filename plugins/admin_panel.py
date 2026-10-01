import asyncio
import html
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from config import Config
from utils.database import db
from utils.helpers import clean_url, mask, ist_str, trial_info
from utils.stats_ui import build_stats_text
from utils.ui import btn, kb, show, edit_by_id

INPUT = {}      # admin_id -> {'field', 'chat', 'msg', 'back'}
PENDING_BC = {}  # admin_id -> {'chat', 'src', 'mins', 'msg'}


def onoff(v):
    return "🟢 ON" if v else "🔴 OFF"


def short(v, n=40):
    v = v or ""
    return html.escape(v if len(v) <= n else v[:n] + "…")


# ================= Screens =================
async def scr_home(s):
    rows = [
        [btn("🔗 Verify setup", "ap:v"), btn("🎁 Trial & Premium", "ap:tp")],
        [btn("⏰ Reminders", "ap:r"), btn("👥 Users", "ap:u")],
        [btn("📣 Broadcast", "ap:bc"), btn("📊 Stats & Files", "ap:st")],
        [btn("⚙️ General", "ap:g")],
        [btn("⬅️ Back", "u:home"), btn("✖️ Close", "ap:close")],
    ]
    return "🛠 <b>ADMIN PANEL</b>\n\n<blockquote>Pick a section below.\nEverything is a button, no commands needed.</blockquote>", kb(rows)


async def scr_verify(s):
    credit = s.get('shortlink_type') == 'credit'
    text = (
        "🔗 <b>VERIFY SETUP</b>\n\n<blockquote>"
        f"Shortlink: <b>{'ON' if s.get('shortlink_status') else 'OFF'}</b> · Mode: <b>{'Credit' if credit else 'Time'}</b>\n"
        f"Bypass guard: <b>{s.get('bypass_time', 15)}s</b> · Web guard: <b>{'ON' if s.get('web_guard') else 'OFF'}</b>\n"
        f"Dual shortner: <b>{'ON' if s.get('dual_shortner') else 'OFF'}</b></blockquote>"
        "\nDual shortner alternates S1 and S2 on each successful verify."
    )
    rows = [
        [btn(f"Shortlink: {onoff(s.get('shortlink_status'))}", "ap:t:sl"),
         btn(f"Mode: {'Credit' if credit else 'Time'}", "ap:t:slt")],
        [btn(f"Credits: {s.get('bypass_credits', 3)}", "ap:c:cred") if credit
         else btn(f"Duration: {s.get('verify_duration', 24)}h", "ap:c:dur"),
         btn(f"Bypass guard: {s.get('bypass_time', 15)}s", "ap:c:byp")],
        [btn(f"Web guard: {onoff(s.get('web_guard'))}", "ap:t:wg"),
         btn(f"Dual: {onoff(s.get('dual_shortner'))}", "ap:t:dual")],
        [btn("🔗 Shortner 1", "ap:s:1"), btn("🔗 Shortner 2", "ap:s:2")],
        [btn("⬅️ Back", "ap:home")],
    ]
    return text, kb(rows)


async def scr_shortner(s, n):
    url, api, tut = db.sl_config(s, int(n))
    text = (
        f"🔗 <b>SHORTNER {n}</b>\n\n<blockquote>"
        f"URL: <code>{html.escape(url) if url else 'not set'}</code>\n"
        f"API: <code>{html.escape(mask(api))}</code>\n"
        f"Tutorial: {short(tut) if tut else 'not set'}</blockquote>"
    )
    rows = [
        [btn("Set URL & API", f"ap:in:sl{n}")],
        [btn("Set tutorial", f"ap:in:tut{n}"), btn("Remove tutorial", f"ap:rt:{n}")],
        [btn("⬅️ Back", "ap:v")],
    ]
    return text, kb(rows)


async def scr_tp(s):
    rows = [
        [btn("🎁 Trial & free links", "ap:tr")],
        [btn("🪙 Plans & prices", "ap:pl"), btn("🧾 Card & payment", "ap:pc")],
        [btn("⬅️ Back", "ap:home")],
    ]
    return "💎 <b>TRIAL & PREMIUM</b>\n\n<blockquote>Choose what you want to edit.</blockquote>", kb(rows)


def stepper(label, key, value):
    return [btn("−", f"ap:n:{key}:-1"), btn(f"{label}: {value}", "ap:noop"), btn("+", f"ap:n:{key}:1")]


async def scr_trial(s):
    text = (
        "🎁 <b>TRIAL & FREE LINKS</b>\n\n<blockquote>"
        f"Trial: <b>{'ON' if s.get('trial_enabled', True) else 'OFF'}</b> · {s.get('trial_days', 3)} days · {s.get('trial_daily', 5)} links/day\n"
        f"After the trial: <b>{s.get('free_daily_limit', 0)}</b> free links/day, then Verify or Premium.</blockquote>"
        "\nTrial days are IST calendar days and start with the user's first file link."
    )
    rows = [
        [btn(f"Trial: {onoff(s.get('trial_enabled', True))}", "ap:t:tri")],
        stepper("Days", "trial_days", s.get('trial_days', 3)),
        stepper("Links/day", "trial_daily", s.get('trial_daily', 5)),
        stepper("Free/day", "free_daily_limit", s.get('free_daily_limit', 0)),
        [btn("⬅️ Back", "ap:tp")],
    ]
    return text, kb(rows)


async def scr_plans(s):
    rows = []
    for p in s.get('premium_plans', []):
        rows.append([btn(f"₹{p['price']} · {p['name']} · {p['days']}d  ✏️", f"ap:in:plan_{p['id']}")])
    rows.append([btn("➕ Add plan", "ap:in:plan_new")])
    rows.append([btn("⬅️ Back", "ap:tp")])
    return "🪙 <b>PLANS & PRICES</b>\n\n<blockquote>Tap a plan to edit or delete it.</blockquote>", kb(rows)


async def scr_card(s):
    def st(k):
        return "✅" if s.get(k) else "—"
    text = (
        "🧾 <b>CARD & PAYMENT</b>\n\n<blockquote>"
        f"UPI: <code>{html.escape(s.get('upi_id', ''))}</code>\n"
        f"Owner: {html.escape(s.get('owner_handle', ''))}\n"
        f"QR image: {short(s.get('qr_url'), 34)}\n"
        f"Links: Info {st('info_link')} · Preview {st('preview_link')} · Proofs {st('proofs_link')} · QR {st('qr_link')}"
        "</blockquote>"
    )
    rows = [
        [btn("Card text (EN)", "ap:in:card_en"), btn("Card text (HI)", "ap:in:card_hi")],
        [btn("UPI ID", "ap:in:upi"), btn("Owner handle", "ap:in:owner")],
        [btn("QR image URL", "ap:in:qr_url"), btn("QR link", "ap:in:qr_link")],
        [btn("Info link", "ap:in:info_link"), btn("Preview link", "ap:in:preview_link")],
        [btn("Proofs link", "ap:in:proofs_link")],
        [btn("⬅️ Back", "ap:tp")],
    ]
    return text, kb(rows)


async def scr_reminders(s):
    text = (
        "⏰ <b>REMINDERS</b>\n\n<blockquote>"
        f"Status: <b>{'ON' if s.get('reminder_enabled', True) else 'OFF'}</b> · every <b>{s.get('reminder_hours', 12)}h</b>\n"
        f"Quiet hours (11 PM – 8 AM IST): <b>{'ON' if s.get('quiet_hours', True) else 'OFF'}</b></blockquote>"
        "\nSent only to users whose trial has ended and who are not verified or premium. "
        "Stops after 5 ignored reminders."
    )
    rows = [
        [btn(f"Reminder: {onoff(s.get('reminder_enabled', True))}", "ap:t:rem"),
         btn(f"Every: {s.get('reminder_hours', 12)}h", "ap:c:rh")],
        [btn(f"Quiet hours: {onoff(s.get('quiet_hours', True))}", "ap:t:qh")],
        [btn("Text (English)", "ap:in:rtext_en"), btn("Text (हिंदी)", "ap:in:rtext_hi")],
        [btn("⬅️ Back", "ap:home")],
    ]
    return text, kb(rows)


async def scr_users(s):
    rows = [
        [btn("Ban", "ap:in:u_ban"), btn("Unban", "ap:in:u_unban")],
        [btn("Add premium", "ap:in:u_addprem"), btn("Remove premium", "ap:in:u_delprem")],
        [btn("Add credits", "ap:in:u_addcred"), btn("Remove credits", "ap:in:u_remcred")],
        [btn("User info", "ap:in:u_info"), btn("Unban all", "ap:cf:unbanall")],
        [btn("⬅️ Back", "ap:home")],
    ]
    return "👥 <b>USERS</b>\n\n<blockquote>Tap an action, then send the user ID when asked.</blockquote>", kb(rows)


async def scr_broadcast(s):
    rows = [
        [btn("Send to all", "ap:in:bc")],
        [btn("Auto-delete 5m", "ap:in:bcd:5"), btn("10m", "ap:in:bcd:10")],
        [btn("30m", "ap:in:bcd:30"), btn("60m", "ap:in:bcd:60")],
        [btn("⬅️ Back", "ap:home")],
    ]
    return "📣 <b>BROADCAST</b>\n\n<blockquote>Choose a mode, then send the message (text, photo, video, anything).</blockquote>", kb(rows)


async def scr_stats(s):
    return await build_stats_text(), kb([[btn("🔄 Refresh", "ap:st"), btn("⬅️ Back", "ap:home")]])


async def scr_general(s):
    ad = s.get('auto_delete', 0)
    text = (
        "⚙️ <b>GENERAL</b>\n\n<blockquote>"
        f"Mode: <b>{s.get('mode', 'public')}</b> · Protect content: <b>{'ON' if s.get('protect_content') else 'OFF'}</b>\n"
        f"Auto-delete: <b>{str(ad) + ' min' if ad else 'OFF'}</b>\n"
        f"DB channel: <code>{s.get('active_db')}</code>\n"
        f"Log channel: <code>{s.get('log_channel')}</code></blockquote>"
        "\nForce-sub channels are managed with /add_fsub, /del_fsub and /fsub_list."
    )
    rows = [
        [btn(f"Mode: {s.get('mode', 'public')}", "ap:t:mode"),
         btn(f"Protect: {onoff(s.get('protect_content'))}", "ap:t:prot")],
        [btn(f"Auto-delete: {str(ad) + 'm' if ad else 'OFF'}", "ap:c:ad")],
        [btn("DB channel", "ap:in:gen_db"), btn("Log channel", "ap:in:gen_log")],
        [btn("⬅️ Back", "ap:home")],
    ]
    return text, kb(rows)


async def build_screen(screen, s):
    name, _, arg = screen.partition(':')
    if name == 's':
        return await scr_shortner(s, arg)
    table = {'home': scr_home, 'v': scr_verify, 'tp': scr_tp, 'tr': scr_trial, 'pl': scr_plans,
             'pc': scr_card, 'r': scr_reminders, 'u': scr_users, 'bc': scr_broadcast,
             'st': scr_stats, 'g': scr_general}
    return await table.get(name, scr_home)(s)


# ================= Toggle / cycle / stepper tables =================
TOGGLES = {  # key -> (setting, default, screen)
    'sl': ('shortlink_status', False, 'v'), 'wg': ('web_guard', False, 'v'), 'dual': ('dual_shortner', False, 'v'),
    'tri': ('trial_enabled', True, 'tr'), 'rem': ('reminder_enabled', True, 'r'), 'qh': ('quiet_hours', True, 'r'),
    'prot': ('protect_content', False, 'g'),
}
CYCLES = {  # key -> (setting, values, default, screen)
    'dur': ('verify_duration', [1, 4, 8, 16, 24, 48], 24, 'v'),
    'cred': ('bypass_credits', [1, 2, 3, 5, 10, 20], 3, 'v'),
    'byp': ('bypass_time', [0, 5, 10, 15, 20, 30, 45, 60], 15, 'v'),
    'rh': ('reminder_hours', [3, 6, 12, 24, 48], 12, 'r'),
    'ad': ('auto_delete', [0, 5, 10, 30, 60, 120], 0, 'g'),
}
STEPPERS = {  # key -> (min, max)
    'trial_days': (1, 30), 'trial_daily': (1, 50), 'free_daily_limit': (0, 50),
}

PROMPTS = {
    'sl1': ("Send the shortner <b>domain and API key</b> separated by a space.\nExample: <code>example.com abc123</code>", 's:1'),
    'sl2': ("Send the shortner <b>domain and API key</b> separated by a space.\nExample: <code>example.com abc123</code>", 's:2'),
    'tut1': ("Send the tutorial link for Shortner 1.", 's:1'),
    'tut2': ("Send the tutorial link for Shortner 2.", 's:2'),
    'rtext_en': ("Send the new <b>English</b> reminder message. HTML formatting is allowed.", 'r'),
    'rtext_hi': ("Send the new <b>Hindi</b> reminder message. HTML formatting is allowed.", 'r'),
    'card_en': ("Send the new <b>English</b> premium card.\nKeep these placeholders: <code>{plans}</code> <code>{upi}</code> <code>{owner}</code>", 'pc'),
    'card_hi': ("Send the new <b>Hindi</b> premium card.\nKeep these placeholders: <code>{plans}</code> <code>{upi}</code> <code>{owner}</code>", 'pc'),
    'upi': ("Send your UPI ID.", 'pc'),
    'owner': ("Send the owner handle, like <code>@NeonGhost</code>.", 'pc'),
    'qr_url': ("Send the QR image link (direct image URL).", 'pc'),
    'qr_link': ("Send the QR button link (or <code>off</code>).", 'pc'),
    'info_link': ("Send the Info link (or <code>off</code>).", 'pc'),
    'preview_link': ("Send the Preview link (or <code>off</code>).", 'pc'),
    'proofs_link': ("Send the Proofs link (or <code>off</code>).", 'pc'),
    'plan_new': ("Send the new plan:\n<code>price days name | हिंदी नाम</code>\nExample: <code>99 30 1 Month | 1 महीना</code>", 'pl'),
    'u_ban': ("Send the <b>user ID</b> to ban.", 'u'),
    'u_unban': ("Send the <b>user ID</b> to unban.", 'u'),
    'u_addprem': ("Send: <code>user_id days</code>", 'u'),
    'u_delprem': ("Send the <b>user ID</b> to remove premium.", 'u'),
    'u_addcred': ("Send: <code>user_id amount</code>", 'u'),
    'u_remcred': ("Send: <code>user_id amount</code>", 'u'),
    'u_info': ("Send the <b>user ID</b>.", 'u'),
    'gen_db': ("Send the DB channel ID, like <code>-100xxxxxxxxxx</code>.", 'g'),
    'gen_log': ("Send the log channel ID, like <code>-100xxxxxxxxxx</code>.", 'g'),
    'bc': ("Send the message to broadcast now.", 'bc'),
}
LINK_FIELDS = {'qr_link': 'qr_link', 'info_link': 'info_link', 'preview_link': 'preview_link', 'proofs_link': 'proofs_link'}


async def render(client, chat_id, msg_id, screen, notice=None):
    s = await db.get_settings()
    text, markup = await build_screen(screen, s)
    if notice:
        text = f"{notice}\n\n{text}"
    await edit_by_id(client, chat_id, msg_id, text, markup)


# ================= Entry points =================
@Client.on_message(filters.command(["settings", "admin", "panel"]) & filters.private)
async def open_panel(client: Client, message: Message):
    if not await db.is_admin(message.from_user.id):
        return
    text, markup = await scr_home(await db.get_settings())
    await message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^close_settings$"))
async def close_settings(client: Client, query: CallbackQuery):
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^ap:"))
async def panel_cb(client: Client, query: CallbackQuery):
    uid = query.from_user.id
    if not await db.is_admin(uid):
        return await query.answer()

    data = query.data[3:]
    act = data.split(':')[0]
    chat_id, msg_id = query.message.chat.id, query.message.id

    if act != 'in':
        INPUT.pop(uid, None)

    if act == 'noop':
        return await query.answer()
    if act == 'close':
        try: await query.message.delete()
        except Exception: pass
        return await query.answer()

    s = await db.get_settings()

    if act == 't':
        key = data.split(':')[1]
        if key == 'slt':
            await db.update_settings('shortlink_type', 'credit' if s.get('shortlink_type') == 'time' else 'time')
            screen = 'v'
        elif key == 'mode':
            await db.update_settings('mode', 'private' if s.get('mode') == 'public' else 'public')
            screen = 'g'
        else:
            setting, default, screen = TOGGLES[key]
            await db.update_settings(setting, not s.get(setting, default))
        await query.answer("Updated")
        return await render(client, chat_id, msg_id, screen)

    if act == 'c':
        setting, values, default, screen = CYCLES[data.split(':')[1]]
        cur = s.get(setting, default)
        nxt = values[(values.index(cur) + 1) % len(values)] if cur in values else values[0]
        await db.update_settings(setting, nxt)
        await query.answer("Updated")
        return await render(client, chat_id, msg_id, screen)

    if act == 'n':
        _, key, delta = data.split(':')
        lo, hi = STEPPERS[key]
        default = {'trial_days': 3, 'trial_daily': 5, 'free_daily_limit': 3}[key]
        val = max(lo, min(hi, int(s.get(key, default)) + int(delta)))
        await db.update_settings(key, val)
        await query.answer()
        return await render(client, chat_id, msg_id, 'tr')

    if act == 'rt':
        n = int(data.split(':')[1])
        await db.update_settings(db.SL_KEYS[n][2], '')
        await query.answer("Tutorial removed")
        return await render(client, chat_id, msg_id, f's:{n}')

    if act == 'cf':
        what = data.split(':')[1]
        if what == 'unbanall':
            rows = kb([[btn("✅ Confirm", "ap:cf:unbanall_go"), btn("✖️ Cancel", "ap:u")]])
            await show(client, query, "Unban <b>all</b> users?", rows)
        elif what == 'unbanall_go':
            count = await db.unban_all_users()
            await query.answer(f"Unbanned {count} users", show_alert=True)
            return await render(client, chat_id, msg_id, 'u')
        return await query.answer()

    if act == 'in':
        parts = data.split(':')
        field = parts[1]
        mins = 0
        if field == 'bcd':
            mins = int(parts[2])
            prompt, back = "Send the message to broadcast. It will auto-delete after "f"<b>{mins} minutes</b>.", 'bc'
        elif field.startswith('plan_') and field != 'plan_new':
            plan = next((p for p in s.get('premium_plans', []) if p['id'] == field[5:]), None)
            if not plan:
                return await query.answer("Plan not found", show_alert=True)
            prompt = ("Editing: <b>₹%s · %s</b>\n\nSend the new details:\n<code>price days name | हिंदी नाम</code>\n"
                      "or send <code>delete</code> to remove this plan." % (plan['price'], html.escape(plan['name'])))
            back = 'pl'
        else:
            prompt, back = PROMPTS[field]
        INPUT[uid] = {'field': field, 'chat': chat_id, 'msg': msg_id, 'back': back, 'mins': mins}
        await show(client, query, f"✏️ {prompt}", kb([[btn("✖️ Cancel", "ap:ic")]]))
        return await query.answer()

    if act == 'ic':
        await query.answer("Cancelled")
        return await render(client, chat_id, msg_id, 'home')

    if act == 'bcgo':
        pb = PENDING_BC.pop(uid, None)
        if not pb:
            return await query.answer("Nothing to send", show_alert=True)
        await query.answer("Broadcasting…")
        asyncio.create_task(run_broadcast(client, pb, chat_id, msg_id))
        return

    await query.answer()
    await show(client, query, *(await build_screen(data, s)), fresh=bool(query.message.photo))


# ================= Text input =================
def parse_plan(text):
    left, _, right = text.partition('|')
    toks = left.split()
    if len(toks) < 3:
        raise ValueError
    price, days = int(toks[0]), int(toks[1])
    if price <= 0 or days <= 0:
        raise ValueError
    name = ' '.join(toks[2:])
    return price, days, name, (right.strip() or name)


async def user_info_text(uid):
    user = await db.get_user(uid)
    if not user:
        return f"No such user: <code>{uid}</code>"
    s = await db.get_settings()
    prem = await db.premium_expire(uid)
    ver = await db.verified_expire(uid)
    info = trial_info(user, s)
    return (
        f"👤 <b>User</b> <code>{uid}</code>\n\n<blockquote>"
        f"Banned: <b>{'yes' if await db.is_banned(uid) else 'no'}</b>\n"
        f"Premium: <b>{('till ' + ist_str(prem)) if prem else 'no'}</b>\n"
        f"Verified: <b>{('till ' + ist_str(ver, '%d %b %I:%M %p')) if ver else 'no'}</b>\n"
        f"Credits: <b>{user.get('credits', 0)}</b>\n"
        f"Trial: <b>{info['phase']}</b>\n"
        f"Language: <b>{user.get('lang', 'en')}</b></blockquote>"
    )


async def apply_input(message: Message, field: str):
    """Returns (error, notice). error=None means success."""
    raw = (message.text or '').strip()
    rich = message.text.html if message.text else ''
    s = await db.get_settings()

    if field in ('sl1', 'sl2'):
        parts = raw.split()
        if len(parts) < 2:
            return "Please send both the domain and the API key.", None
        url = parts[0].strip("<>[]()\"' ").replace("https://", "").replace("http://", "").rstrip("/")
        api = parts[1].strip("<>[]()\"' ")
        ku, ka, _ = db.SL_KEYS[int(field[-1])]
        await db.update_settings(ku, url)
        await db.update_settings(ka, api)
        return None, "✅ Shortner saved."

    if field in ('tut1', 'tut2'):
        ktut = db.SL_KEYS[int(field[-1])][2]
        await db.update_settings(ktut, '' if raw.lower() == 'off' else raw.strip("<>[]()\"' "))
        return None, "✅ Tutorial saved."

    if field in ('rtext_en', 'rtext_hi'):
        await db.update_settings('reminder_text' if field == 'rtext_en' else 'reminder_text_hi', rich)
        return None, "✅ Reminder text saved."

    if field in ('card_en', 'card_hi'):
        if '{plans}' not in raw:
            return "The card must contain the {plans} placeholder.", None
        await db.update_settings('premium_card' if field == 'card_en' else 'premium_card_hi', rich)
        return None, "✅ Card saved."

    if field == 'upi':
        await db.update_settings('upi_id', raw)
        return None, "✅ UPI saved."
    if field == 'owner':
        await db.update_settings('owner_handle', raw if raw.startswith('@') else '@' + raw)
        return None, "✅ Owner saved."
    if field == 'qr_url':
        await db.update_settings('qr_url', clean_url(raw))
        await db.update_settings('qr_file_id', None)
        return None, "✅ QR image saved."
    if field in LINK_FIELDS:
        await db.update_settings(LINK_FIELDS[field], '' if raw.lower() == 'off' else clean_url(raw))
        return None, "✅ Link saved."

    if field == 'plan_new' or field.startswith('plan_'):
        plans = list(s.get('premium_plans', []))
        if field != 'plan_new' and raw.lower() == 'delete':
            plans = [p for p in plans if p['id'] != field[5:]]
            await db.update_settings('premium_plans', plans)
            return None, "🗑 Plan deleted."
        try:
            price, days, name, name_hi = parse_plan(raw)
        except ValueError:
            return "Format: price days name | हिंदी नाम  (example: 99 30 1 Month | 1 महीना)", None
        if field == 'plan_new':
            nums = [int(p['id'][1:]) for p in plans if p['id'][1:].isdigit()]
            plans.append({'id': f"p{(max(nums) if nums else 0) + 1}", 'name': name, 'name_hi': name_hi, 'price': price, 'days': days})
        else:
            for p in plans:
                if p['id'] == field[5:]:
                    p.update({'name': name, 'name_hi': name_hi, 'price': price, 'days': days})
        await db.update_settings('premium_plans', plans)
        return None, "✅ Plan saved."

    if field in ('gen_db', 'gen_log'):
        try:
            cid = int(raw)
        except ValueError:
            return "Channel ID must be a number.", None
        await db.update_settings('active_db' if field == 'gen_db' else 'log_channel', cid)
        return None, "✅ Channel saved."

    if field.startswith('u_'):
        parts = raw.split()
        try:
            uid = int(parts[0])
            if field == 'u_ban':
                if uid == Config.OWNER_ID:
                    return "You cannot ban the owner.", None
                await db.ban_user(uid)
                return None, f"🚫 Banned <code>{uid}</code>"
            if field == 'u_unban':
                await db.unban_user(uid)
                return None, f"✅ Unbanned <code>{uid}</code>"
            if field == 'u_delprem':
                await db.remove_premium(uid)
                return None, f"🗑 Premium removed for <code>{uid}</code>"
            if field == 'u_info':
                return None, await user_info_text(uid)
            amount = int(parts[1])
            if field == 'u_addprem':
                exp = await db.extend_premium(uid, amount)
                return None, f"💎 Premium for <code>{uid}</code> till {ist_str(exp)}"
            if field == 'u_addcred':
                await db.add_credits(uid, amount)
                return None, f"✅ Added {amount} credits to <code>{uid}</code>"
            if field == 'u_remcred':
                cur = await db.get_credits(uid)
                await db.add_credits(uid, -min(cur, amount))
                return None, f"✅ Removed credits from <code>{uid}</code>"
        except (ValueError, IndexError):
            return "Please send the numbers in the format shown.", None
    return "Unknown field.", None


@Client.on_message(filters.private & filters.incoming, group=-3)
async def admin_input_router(client: Client, message: Message):
    if not message.from_user:
        return
    uid = message.from_user.id
    st = INPUT.get(uid)
    if not st:
        return

    if message.text and message.text.startswith('/'):
        INPUT.pop(uid, None)
        if message.command and message.command[0] == 'cancel':
            await render(client, st['chat'], st['msg'], 'home', "Cancelled.")
            message.stop_propagation()
        return  # another command: drop the pending input and let it run

    field = st['field']
    if field in ('bc', 'bcd'):
        INPUT.pop(uid, None)
        PENDING_BC[uid] = {'chat': message.chat.id, 'src': message.id, 'mins': st.get('mins', 0)}
        total = await db.total_users()
        extra = f" · auto-delete after {st['mins']} min" if st.get('mins') else ""
        text = f"📣 <b>Ready to broadcast</b> to <b>{total}</b> users{extra}.\n\nSend it now?"
        await edit_by_id(client, st['chat'], st['msg'], text, kb([[btn("✅ Confirm", "ap:bcgo"), btn("✖️ Cancel", "ap:bc")]]))
        message.stop_propagation()

    if not message.text:
        await message.reply_text("Please send text for this field, or tap Cancel.")
        message.stop_propagation()

    error, notice = await apply_input(message, field)
    if error:
        await message.reply_text(f"⚠️ {error}")
        message.stop_propagation()

    INPUT.pop(uid, None)
    try:
        await message.delete()
    except Exception:
        pass
    if field == 'u_info':
        await edit_by_id(client, st['chat'], st['msg'], notice, kb([[btn("⬅️ Back", "ap:u")]]))
    else:
        await render(client, st['chat'], st['msg'], st['back'], notice)
    message.stop_propagation()


# ================= Broadcast =================
async def _delete_later(client, chat_id, msg_id, delay):
    await asyncio.sleep(delay)
    try:
        await client.delete_messages(chat_id, msg_id)
    except Exception:
        pass


async def run_broadcast(client: Client, pb: dict, panel_chat: int, panel_msg: int):
    sent = failed = 0
    batch = []

    async def one(uid):
        nonlocal sent, failed
        for _ in range(2):
            try:
                m = await client.copy_message(uid, pb['chat'], pb['src'])
                sent += 1
                if pb['mins']:
                    asyncio.create_task(_delete_later(client, uid, m.id, pb['mins'] * 60))
                return
            except FloodWait as e:
                await asyncio.sleep(e.value + 1)
            except Exception:
                break
        failed += 1

    async def flush():
        if batch:
            await asyncio.gather(*[one(u) for u in batch])
            batch.clear()
            await asyncio.sleep(1)  # ~25 messages per second, safely under Telegram limits

    done = 0
    async for doc in db.users_col.find({}, {'_id': 1}):
        batch.append(doc['_id'])
        if len(batch) >= 25:
            await flush()
            done += 25
            if done % 250 == 0:
                await edit_by_id(client, panel_chat, panel_msg, f"📣 Broadcasting… {sent} sent · {failed} failed")
    await flush()
    await edit_by_id(client, panel_chat, panel_msg,
                     f"✅ <b>Broadcast finished</b>\n\n🟢 Sent: <b>{sent}</b>\n🔴 Failed/blocked: <b>{failed}</b>",
                     kb([[btn("⬅️ Back", "ap:bc")]]))
