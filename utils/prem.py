"""Shared premium helpers and screens (used by plugins/premium.py and plugins/admin_panel.py)."""
import html
import time
from config import Config
from utils.database import db
from utils.helpers import clean_url, ist_str
from utils.i18n import tr, PREMIUM_CARD_EN, PREMIUM_CARD_HI, PREMIUM_SOLO_EN, PREMIUM_SOLO_HI
from utils.ui import btn, kb

PER_PAGE = 8


# ---------------- basics ----------------
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


def contact_row(settings, lang):
    """Full-width 'Contact Owner' button as a list of rows ([] when no contact is configured)."""
    url = owner_url(settings)
    return [[btn(tr(lang, 'b_contact_owner'), url=url)]] if url else []


def sync_active(settings):
    return bool(settings.get('sync_enabled') and settings.get('sync_url') and settings.get('partner_username'))


# ---------------- user-facing plans screen ----------------
def render_card(settings, lang, me=None):
    custom = settings.get('card_custom_hi' if lang == 'hi' else 'card_custom_en')
    duo = bool(sync_active(settings) and me)
    if custom:
        tpl = custom
    elif duo:
        tpl = PREMIUM_CARD_HI if lang == 'hi' else PREMIUM_CARD_EN
    else:
        tpl = PREMIUM_SOLO_HI if lang == 'hi' else PREMIUM_SOLO_EN
    partner = (settings.get('partner_username') or '').lstrip('@')
    bots = f"✅ @{me}\n✅ @{partner}" if duo else ""
    plans = "\n".join(f"🪙 ₹{p['price']} — {html.escape(plan_name(p, lang))}" for p in settings.get('premium_plans', []))
    return (tpl.replace('{bots}', bots)
               .replace('{plans}', plans)
               .replace('{upi}', html.escape(settings.get('upi_id', '')))
               .replace('{owner}', html.escape(settings.get('owner_handle', ''))))


def plans_view(settings, lang, me=None):
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
    rows.extend(contact_row(settings, lang))          # always the last, full-width row
    return render_card(settings, lang, me), kb(rows)


# ---------------- admin: pending payments ----------------
def fmt_age(sec):
    sec = max(int(sec), 0)
    if sec < 60:
        return "just now"
    if sec < 3600:
        return f"{sec // 60}m ago"
    if sec < 86400:
        return f"{sec // 3600}h ago"
    return f"{sec // 86400}d ago"


async def pending_view():
    docs = await db.pending_list(6)
    total = await db.pending_count()
    if not docs:
        return ("💳 <b>PENDING PAYMENTS</b>\n\n<blockquote>No pending payments. All clear ✅</blockquote>",
                kb([[btn("🔄 Refresh", "ap:pp"), btn("⬅️ Back", "ap:home")]]))
    s = await db.get_settings()
    now = int(time.time())
    lines, rows = [], []
    for i, d in enumerate(docs, 1):
        plan = find_plan(s, d.get('plan'))
        label = plan_label(plan) if plan else f"₹{d.get('price', '?')}"
        lines.append(f"<b>{i}.</b> <a href=\"tg://user?id={d['u']}\">{d['u']}</a> · {html.escape(label)} · {fmt_age(now - d.get('ts', now))}")
        rows.append([btn(f"✅ #{i} {label}", f"payok:{d['_id']}:{d['plan']}"), btn(f"❌ #{i}", f"payno:{d['_id']}")])
    more = f"\n<i>Showing {len(docs)} of {total}.</i>" if total > len(docs) else ""
    text = ("💳 <b>PENDING PAYMENTS</b>\n\n<blockquote>" + "\n".join(lines) + "</blockquote>" + more +
            "\n\n<i>To approve a different plan, use the original message in your chat.</i>")
    rows.append([btn("🔄 Refresh", "ap:pp"), btn("⬅️ Back", "ap:home")])
    return text, kb(rows)


# ---------------- admin: premium list ----------------
def left_text(seconds):
    seconds = max(int(seconds), 0)
    d, h = seconds // 86400, (seconds % 86400) // 3600
    return f"{d}d left" if d else f"{h}h left"


async def premium_list_view(client, tab='active', page=0):
    tab = tab if tab in ('active', 'soon') else 'active'
    active, soon = await db.premium_counts()
    total = active if tab == 'active' else soon
    pages = max(1, -(-total // PER_PAGE))
    page = min(max(int(page), 0), pages - 1)
    docs = await db.premium_docs(tab, page, PER_PAGE)

    names = {}
    ids = [d['_id'] for d in docs]
    if ids:
        try:
            got = await client.get_users(ids)
            for u in (got if isinstance(got, list) else [got]):
                names[u.id] = (u.first_name or "").strip()
        except Exception:
            pass

    now = int(time.time())
    lines = []
    for n, d in enumerate(docs, page * PER_PAGE + 1):
        uid = d['_id']
        shown = html.escape(names.get(uid) or str(uid))
        lines.append(f"<b>{n}.</b> <a href=\"tg://user?id={uid}\">{shown}</a> · <code>{uid}</code>\n"
                     f"     ⏳ {ist_str(d['expire_at'])} · {left_text(d['expire_at'] - now)}")
    body = "\n".join(lines) if lines else "No premium users here yet."
    text = (f"💎 <b>PREMIUM USERS</b>\n\n<blockquote>✅ Active: <b>{active}</b> · ⏰ Expiring in 3 days: <b>{soon}</b></blockquote>\n\n"
            f"{body}")

    rows = [[btn(("• " if tab == 'active' else "") + f"Active ({active})", "ap:pr:active:0"),
             btn(("• " if tab == 'soon' else "") + f"Expiring ({soon})", "ap:pr:soon:0")]]
    if pages > 1:
        nav = []
        if page > 0:
            nav.append(btn("⬅️ Prev", f"ap:pr:{tab}:{page - 1}"))
        nav.append(btn(f"{page + 1}/{pages}", "ap:noop"))
        if page < pages - 1:
            nav.append(btn("Next ➡️", f"ap:pr:{tab}:{page + 1}"))
        rows.append(nav)
    rows.append([btn("⬅️ Back", "ap:u")])
    return text, kb(rows)
