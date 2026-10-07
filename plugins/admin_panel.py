import asyncio
import html
import re
import time
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from config import Config
from utils.database import db
from utils.helpers import clean_url, mask, ist_str, trial_info, week_key
from utils.referral import MEDALS, prizes_text
from utils.stats_ui import build_stats_text
from utils.prem import premium_list_view, pending_view, fmt_age
from utils.proof import post_proof
from utils import sync as syncmod
from utils.ui import btn, kb, show, edit_by_id

INPUT = {}      # admin_id -> {'field', 'chat', 'msg', 'back'}
PENDING_BC = {}  # admin_id -> {'chat', 'src', 'mins', 'target'}
BC = {'mins': 0}  # broadcast auto-delete minutes (single owner/admin)
BC_LABELS = {'all': 'all users', 'prem': 'premium users (past + current)', 'ver': 'verified users (past + current)'}


def onoff(v):
    return "🟢 ON" if v else "🔴 OFF"


def short(v, n=40):
    v = v or ""
    return html.escape(v if len(v) <= n else v[:n] + "…")


# ================= Screens =================
async def scr_home(s):
    pend = await db.pending_count()
    pay_label = f"💳 Pending payments ({pend})" if pend else "💳 Pending payments"
    rows = [
        [btn("🔗 Verify setup", "ap:v"), btn("🎁 Trial & Premium", "ap:tp")],
        [btn("⏰ Reminders", "ap:r"), btn("👥 Users", "ap:u")],
        [btn("📣 Broadcast", "ap:bc"), btn("📊 Stats & Files", "ap:st")],
        [btn(pay_label, "ap:pp")],
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
        [btn("🔗 Partner bot", "ap:pt"), btn("📢 Proof channel", "ap:pf")],
        [btn("🎁 Refer & Earn", "ap:rf")],
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
        [btn("💎 Premium list", "ap:pr:active:0")],
        [btn("Ban", "ap:in:u_ban"), btn("Unban", "ap:in:u_unban")],
        [btn("Add premium", "ap:in:u_addprem"), btn("Remove premium", "ap:in:u_delprem")],
        [btn("Add credits", "ap:in:u_addcred"), btn("Remove credits", "ap:in:u_remcred")],
        [btn("User info", "ap:in:u_info"), btn("Unban all", "ap:cf:unbanall")],
        [btn("⬅️ Back", "ap:home")],
    ]
    return "👥 <b>USERS</b>\n\n<blockquote>Tap an action, then send the user ID when asked.</blockquote>", kb(rows)


async def scr_broadcast(s):
    n_all, n_prem, n_ver = await db.target_count('all'), await db.target_count('prem'), await db.target_count('ver')
    mins = BC['mins']
    text = ("📣 <b>BROADCAST</b>\n\n<blockquote>Pick who gets it, then send the message (text, photo, video, anything).\n"
            f"Auto-delete: <b>{str(mins) + ' min' if mins else 'OFF'}</b></blockquote>")
    rows = [
        [btn(f"👥 All users ({n_all})", "ap:in:bc:all")],
        [btn(f"💎 Premium ({n_prem})", "ap:in:bc:prem"), btn(f"✅ Verified ({n_ver})", "ap:in:bc:ver")],
        [btn(f"🗑 Auto-delete: {str(mins) + 'm' if mins else 'OFF'}", "ap:bm")],
        [btn("⬅️ Back", "ap:home")],
    ]
    return text, kb(rows)


async def scr_proof(s):
    chat = int(s.get('proof_chat') or 0)
    on = s.get('proof_enabled', True)
    text = (
        "📢 <b>PROOF CHANNEL</b>\n\n<blockquote>"
        f"Status: <b>{'ON' if on else 'OFF'}</b>{'' if chat else ' (no channel set yet)'}\n"
        f"Channel ID: <code>{chat or 'not set'}</code>\n"
        f"Caption: <b>{'custom' if s.get('proof_caption') else 'default'}</b></blockquote>\n\n"
        "<i>When you approve a payment, its screenshot is posted here with the member's name, plan and validity, "
        "plus Buy Premium and Contact buttons. Make this bot an admin of the channel. On every payment request "
        "you can switch the post OFF before approving.</i>"
    )
    rows = [
        [btn(f"Proof: {onoff(on)}", "ap:t:proof")],
        [btn("Channel ID", "ap:in:proof_chat"), btn("Caption", "ap:in:proof_cap")],
        [btn("🧪 Send test post", "ap:xt")],
        [btn("⬅️ Back", "ap:tp")],
    ]
    return text, kb(rows)


async def scr_refer(s):
    async def board(rows):
        if not rows:
            return "—"
        lines = []
        for i, (u, n) in enumerate(rows):
            lines.append(f"{MEDALS[i]} {html.escape(await db.display_name(u))} (<code>{u}</code>) · {n}")
        return "\n".join(lines)
    today, life = await db.ref_today_count(), await db.ref_lifetime_count()
    week_top = await db.ref_top(week_key(), 5)
    life_top = await db.ref_top(None, 5, qualified=False)
    text = (
        "🎁 <b>REFER & EARN</b>\n\n<blockquote>"
        f"Status: <b>{'ON' if s.get('ref_enabled', True) else 'OFF'}</b>\n"
        f"Reward: every <b>{s.get('ref_need', 5)}</b> referrals = <b>{s.get('ref_days', 1)}</b> day(s) Premium\n"
        f"Weekly bonus: {prizes_text(s)}\n\n"
        f"New users via share today: <b>{today}</b>\nLifetime: <b>{life}</b></blockquote>\n\n"
        f"🏆 <b>This week (active friends)</b>\n{await board(week_top)}\n\n"
        f"🏅 <b>Lifetime top 5</b>\n{await board(life_top)}\n\n"
        "<i>Keep these numbers the same in both bots. A referral is active once the friend receives a file. Banned users are never listed.</i>"
    )
    rows = [
        [btn(f"Refer: {onoff(s.get('ref_enabled', True))}", "ap:t:refer")],
        stepper("Every", "ref_need", s.get('ref_need', 5)),
        stepper("Days", "ref_days", s.get('ref_days', 1)),
        [btn("🏅 Weekly bonus days", "ap:in:ref_weekly")],
        [btn("⬅️ Back", "ap:tp")],
    ]
    return text, kb(rows)


async def scr_partner(s):
    on = bool(s.get('sync_enabled'))
    pend = await db.sync_pending_count()
    last = s.get('sync_last_ok', 0)
    err = s.get('sync_err')
    status = f"⚠️ {html.escape(err)}" if err else ("✅ OK" if (on and last) else "—")
    partner = s.get('partner_username')
    tick = s.get('sync_tick', 0)
    worker = (f"✅ running ({fmt_age(time.time() - tick)})" if tick and time.time() - tick < 120
              else ("❌ not running" if tick else "⏳ starting"))
    seen = await syncmod.partner_seen(s)
    if seen is None:
        pw = "—"
    elif seen == 0:
        pw = "❌ not seen yet (open its Partner screen and turn Sync ON)"
    elif time.time() - seen < 120:
        pw = f"✅ active ({fmt_age(time.time() - seen)})"
    else:
        pw = f"⚠️ last seen {fmt_age(time.time() - seen)}"
    text = (
        "🔗 <b>PARTNER BOT</b>\n\n<blockquote>"
        f"Sync: <b>{'ON' if on else 'OFF'}</b>\n"
        f"Mailbox: <code>{html.escape(syncmod.host_of(s.get('sync_url')))}</code>\n"
        f"DB name: <code>{html.escape(s.get('sync_db') or 'sync_mailbox')}</code>\n"
        f"Partner: {'@' + html.escape(partner) if partner else 'not set'}\n"
        f"This bot's worker: {worker}\n"
        f"Partner bot's worker: {pw}\n"
        f"Waiting to send: <b>{pend}</b> · Last sync: <b>{fmt_age(time.time() - last) if last else 'never'}</b>\n"
        f"Status: {status}</blockquote>\n\n"
        "<i>Premium you give here is also given in the partner bot. "
        "Both bots must use the same Mailbox URL and DB name. Only grants are synced, never removals.</i>"
    )
    rows = [
        [btn(f"Sync: {onoff(on)}", "ap:t:sync")],
        [btn("Mailbox URL", "ap:in:sync_url"), btn("DB name", "ap:in:sync_db")],
        [btn("Partner @username", "ap:in:sync_partner"), btn("🧪 Test connection", "ap:tc")],
        [btn("🔄 Sync now", "ap:sn")],
        [btn("⬅️ Back", "ap:tp")],
    ]
    return text, kb(rows)


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
        [btn(f"Auto-delete: {str(ad) + 'm' if ad else 'OFF'}", "ap:c:ad"),
         btn(f"Share button: {onoff(s.get('share_button', True))}", "ap:t:share")],
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
             'st': scr_stats, 'g': scr_general, 'pt': scr_partner, 'pf': scr_proof, 'rf': scr_refer}
    return await table.get(name, scr_home)(s)


# ================= Toggle / cycle / stepper tables =================
TOGGLES = {  # key -> (setting, default, screen)
    'sl': ('shortlink_status', False, 'v'), 'wg': ('web_guard', False, 'v'), 'dual': ('dual_shortner', False, 'v'),
    'tri': ('trial_enabled', True, 'tr'), 'rem': ('reminder_enabled', True, 'r'), 'qh': ('quiet_hours', True, 'r'),
    'prot': ('protect_content', False, 'g'),
    'share': ('share_button', True, 'g'),
    'proof': ('proof_enabled', True, 'pf'),
    'refer': ('ref_enabled', True, 'rf'),
}
CYCLES = {  # key -> (setting, values, default, screen)
    'dur': ('verify_duration', [1, 4, 8, 16, 24, 48], 24, 'v'),
    'cred': ('bypass_credits', [1, 2, 3, 5, 10, 20], 3, 'v'),
    'byp': ('bypass_time', [0, 5, 10, 15, 20, 30, 45, 60], 15, 'v'),
    'rh': ('reminder_hours', [3, 6, 12, 24, 48], 12, 'r'),
    'ad': ('auto_delete', [0, 5, 10, 30, 60, 120], 0, 'g'),
}
STEPPERS = {  # key -> (min, max)
    'trial_days': (1, 30), 'trial_daily': (1, 50), 'free_daily_limit': (0, 50), 'ref_need': (1, 100), 'ref_days': (1, 365),
}

PROMPTS = {
    'sl1': ("Send the shortner <b>domain and API key</b> separated by a space.\nExample: <code>example.com abc123</code>", 's:1'),
    'sl2': ("Send the shortner <b>domain and API key</b> separated by a space.\nExample: <code>example.com abc123</code>", 's:2'),
    'tut1': ("Send the tutorial link for Shortner 1.", 's:1'),
    'tut2': ("Send the tutorial link for Shortner 2.", 's:2'),
    'rtext_en': ("Send the new <b>English</b> reminder message. HTML formatting is allowed.", 'r'),
    'rtext_hi': ("Send the new <b>Hindi</b> reminder message. HTML formatting is allowed.", 'r'),
    'card_en': ("Send the new <b>English</b> premium message (shown when a user taps Premium).\nPlaceholders: <code>{bots}</code> <code>{plans}</code> <code>{upi}</code> <code>{owner}</code>\nSend <code>default</code> to go back to the built-in text.", 'pc'),
    'card_hi': ("Send the new <b>Hindi</b> premium message (shown when a user taps Premium).\nPlaceholders: <code>{bots}</code> <code>{plans}</code> <code>{upi}</code> <code>{owner}</code>\nSend <code>default</code> to go back to the built-in text.", 'pc'),
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
    'sync_url': ("Send the <b>Mailbox MongoDB URL</b> (starts with <code>mongodb</code>). Both bots must use the same one. Your message is deleted right after.", 'pt'),
    'sync_db': ("Send the <b>Mailbox DB name</b> (letters, numbers, _ or -). Both bots must use the same name. Default: <code>sync_mailbox</code>", 'pt'),
    'proof_chat': ("Send the <b>proof channel ID</b>, like <code>-100xxxxxxxxxx</code>. This bot must be an admin there.", 'pf'),
    'proof_cap': ("Send the new proof caption (HTML allowed).\nPlaceholders: <code>{name}</code> <code>{plan}</code> <code>{days}</code> <code>{bots}</code>\nSend <code>default</code> to go back to the built-in caption.", 'pf'),
    'ref_weekly': ("Send the weekly bonus days for rank 1 to 5, separated by spaces.\nExample: <code>10 8 6 4 2</code>", 'rf'),
    'sync_partner': ("Send the <b>partner bot's @username</b>.", 'pt'),
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
        elif key == 'sync':
            if not s.get('sync_enabled') and not s.get('sync_url'):
                return await query.answer("Set the Mailbox URL first.", show_alert=True)
            await db.update_settings('sync_enabled', not s.get('sync_enabled', False))
            screen = 'pt'
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
        default = {'trial_days': 3, 'trial_daily': 5, 'free_daily_limit': 3, 'ref_need': 5, 'ref_days': 1}[key]
        val = max(lo, min(hi, int(s.get(key, default)) + int(delta)))
        await db.update_settings(key, val)
        await query.answer()
        return await render(client, chat_id, msg_id, 'rf' if key.startswith('ref_') else 'tr')

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

    if act == 'pr':
        _, tab, page = data.split(':')
        text, markup = await premium_list_view(client, tab, int(page))
        await query.answer()
        return await show(client, query, text, markup)

    if act == 'pp':
        text, markup = await pending_view()
        await query.answer()
        return await show(client, query, text, markup)

    if act == 'tc':
        ok, info = await syncmod.test_connection(client)
        await query.answer("Connected ✅" if ok else "Connection failed ❌", show_alert=not ok)
        return await render(client, chat_id, msg_id, 'pt', ("✅ " if ok else "⚠️ ") + html.escape(info))

    if act == 'xt':
        chat = int(s.get('proof_chat') or 0)
        if not chat:
            return await query.answer("Set the channel ID first.", show_alert=True)
        plan = (s.get('premium_plans') or [{'name': '1 Month', 'days': 30}])[0]
        posted, err = await post_proof(client, s, {'name': 'Test Member'}, plan)
        await query.answer("Posted ✅" if posted else "Failed ❌", show_alert=not posted)
        note = "✅ Test post sent to the channel." if posted else f"⚠️ Could not post ({html.escape(err)}). Make this bot an admin there and check the ID."
        return await render(client, chat_id, msg_id, 'pf', note)

    if act == 'sn':
        try:
            sent, got = await syncmod.sync_once(client, force=True)
            note = f"✅ Sync done. Sent {sent} · Received {got}"
            if not s.get('sync_enabled'):
                note += "\n⚠️ Sync is still OFF, so this only runs when you tap this button."
        except Exception as e:
            note = f"⚠️ {html.escape(type(e).__name__)}: {html.escape(str(e)[:120])}"
        await query.answer("Done")
        return await render(client, chat_id, msg_id, 'pt', note)

    if act == 'bm':
        vals = [0, 5, 10, 30, 60]
        BC['mins'] = vals[(vals.index(BC['mins']) + 1) % len(vals)] if BC['mins'] in vals else 0
        await query.answer()
        return await render(client, chat_id, msg_id, 'bc')

    if act == 'in':
        parts = data.split(':')
        field = parts[1]
        mins = 0
        target = 'all'
        if field == 'bc':
            target = parts[2] if len(parts) > 2 and parts[2] in db.BC_FILTERS else 'all'
            mins = BC['mins']
            extra = f" It will auto-delete after <b>{mins} minutes</b>." if mins else ""
            prompt, back = f"Send the message to broadcast to <b>{BC_LABELS[target]}</b>.{extra}", 'bc'
        elif field.startswith('plan_') and field != 'plan_new':
            plan = next((p for p in s.get('premium_plans', []) if p['id'] == field[5:]), None)
            if not plan:
                return await query.answer("Plan not found", show_alert=True)
            prompt = ("Editing: <b>₹%s · %s</b>\n\nSend the new details:\n<code>price days name | हिंदी नाम</code>\n"
                      "or send <code>delete</code> to remove this plan." % (plan['price'], html.escape(plan['name'])))
            back = 'pl'
        else:
            prompt, back = PROMPTS[field]
        INPUT[uid] = {'field': field, 'chat': chat_id, 'msg': msg_id, 'back': back, 'mins': mins, 'target': target}
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
        key = 'card_custom_en' if field == 'card_en' else 'card_custom_hi'
        await db.update_settings(key, '' if raw.lower() == 'default' else rich)
        return None, "✅ Card saved."

    if field == 'sync_url':
        if not raw.startswith('mongodb'):
            return "The URL must start with mongodb:// or mongodb+srv://", None
        syncmod.forget_client()
        await db.update_settings('sync_url', raw)
        return None, "✅ Mailbox URL saved. Now tap Test connection."
    if field == 'sync_db':
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,60}', raw):
            return "Use only letters, numbers, _ or - (max 60 characters).", None
        syncmod.forget_client()
        await db.update_settings('sync_db', raw)
        return None, "✅ DB name saved."
    if field == 'sync_partner':
        name = raw.lstrip('@')
        if not re.fullmatch(r'[A-Za-z0-9_]{4,32}', name):
            return "That does not look like a bot username.", None
        await db.update_settings('partner_username', name)
        return None, "✅ Partner saved."

    if field == 'proof_chat':
        try:
            cid = int(raw)
        except ValueError:
            return "Channel ID must be a number like -100123456789.", None
        await db.update_settings('proof_chat', cid)
        return None, "✅ Proof channel saved."
    if field == 'proof_cap':
        await db.update_settings('proof_caption', '' if raw.lower() == 'default' else rich)
        return None, "✅ Caption saved."

    if field == 'ref_weekly':
        try:
            days = [int(x) for x in raw.split()]
            if not 1 <= len(days) <= 5 or any(d < 0 or d > 365 for d in days):
                raise ValueError
        except ValueError:
            return "Send 1 to 5 numbers (0 to 365), like: 10 8 6 4 2", None
        await db.update_settings('ref_weekly', days)
        return None, "✅ Weekly bonus saved."

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
                queued = await db.sync_queue(uid, amount, f"m{uid}_{int(time.time())}")
                return None, f"💎 Premium for <code>{uid}</code> till {ist_str(exp)}" + (" · sent to partner bot" if queued else "")
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
    if field == 'bc':
        INPUT.pop(uid, None)
        target = st.get('target', 'all')
        PENDING_BC[uid] = {'chat': message.chat.id, 'src': message.id, 'mins': st.get('mins', 0), 'target': target}
        total = await db.target_count(target)
        extra = f" · auto-delete after {st['mins']} min" if st.get('mins') else ""
        text = f"📣 <b>Ready to broadcast</b> to <b>{total}</b> {BC_LABELS[target]}{extra}.\n\nSend it now?"
        await edit_by_id(client, st['chat'], st['msg'], text, kb([[btn("✅ Confirm", "ap:bcgo"), btn("✖️ Cancel", "ap:bc")]]))
        message.stop_propagation()

    if not message.text:
        await message.reply_text("Please send text for this field, or tap Cancel.")
        message.stop_propagation()

    error, notice = await apply_input(message, field)
    if error:
        if field == 'sync_url':
            try:
                await message.delete()  # never leave a database URL lying in the chat
            except Exception:
                pass
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
    async for doc in db.users_col.find(db.BC_FILTERS.get(pb.get('target', 'all'), {}), {'_id': 1}):
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
