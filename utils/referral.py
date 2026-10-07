"""Refer & Earn: tracking, rewards (every N referrals) and the weekly top-5 prizes.

Referral counts are shared between both bots through the partner-sync mailbox: every new referral
becomes a small event that both bots store, so both bots show the same numbers and both grant the
same rewards to their own premium list (no extra premium sync is needed for rewards).
"""
import asyncio
import html
import re
import time
from urllib.parse import quote
from pyrogram.enums import ParseMode
from pyrogram.types import LinkPreviewOptions
from utils.database import db
from utils.helpers import ist_str, week_key, week_start_ts
from utils.i18n import tr
from utils.ui import btn, kb, more_row

RE_RF = re.compile(r'^(.+)_rf(\d{5,12})$')
MEDALS = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']


# ---------------- links ----------------
def parse_start(payload):
    """'abc_rf123456789' -> ('abc', 123456789); 'ref_123456789' -> ('', 123456789); anything else unchanged."""
    if not payload:
        return payload, None
    if payload.startswith('ref_') and payload[4:].isdigit() and 5 <= len(payload[4:]) <= 12:
        return '', int(payload[4:])
    m = RE_RF.match(payload)
    if m:
        return m.group(1), int(m.group(2))
    return payload, None


def ref_link(bot_username, uid):
    return f"https://t.me/{bot_username}?start=ref_{uid}"


def share_link(bot_username, payload, uid):
    """The post link with the sharer's id attached (Telegram allows 64 characters; if too long, share it untracked)."""
    tagged = f"{payload}_rf{uid}"
    return f"https://t.me/{bot_username}?start={tagged if len(tagged) <= 64 else payload}"


def share_url(link, text):
    return "https://t.me/share/url?url=" + quote(link, safe='') + "&text=" + quote(text, safe='')


# ---------------- notifications ----------------
async def notify(client, uid, key, **kw):
    user = await db.get_user(uid) or {}
    lang = user.get('lang') or 'en'
    settings = await db.get_settings()
    rows = [[btn(tr(lang, 'b_refer'), 'u:refer')]] + more_row(settings, lang)
    try:
        await client.send_message(uid, tr(lang, key, **kw), reply_markup=kb(rows), parse_mode=ParseMode.HTML,
                                  link_preview_options=LinkPreviewOptions(is_disabled=True))
    except Exception:
        pass  # user never started this bot / blocked it: the premium days are still added


# ---------------- counting + rewards ----------------
async def apply_milestone(client, by, total, settings):
    need = int(settings.get('ref_need', 5) or 0)
    days = int(settings.get('ref_days', 1) or 0)
    if need <= 0 or days <= 0 or total % need != 0:
        return False
    if not await db.claim_reward(f"m_{by}_{total}", by, days, 'milestone'):
        return False
    exp = await db.extend_premium(by, days)
    print(f"🎁 Referral reward: {days} day(s) premium to {by} ({total} referrals)")
    await notify(client, by, 'ref_reward', total=total, days=days, need=need, date=ist_str(exp))
    return True


async def handle_new_referral(client, new_user, by, settings):
    """Called from /start for a brand-new user who arrived through someone's link."""
    if not settings.get('ref_enabled', True) or not by or by == new_user:
        return False
    if await db.is_banned(by) or not await db.users_col.find_one({'_id': by}):
        return False
    ts = int(time.time())
    wk = week_key(ts)
    inserted, total = await db.record_referral(new_user, by, wk, ts)
    if not inserted:
        return False
    if await db.sync_queue_event(f"rf_{new_user}", {'kind': 'ref', 'u': new_user, 'by': by, 'wk': wk, 'ts': ts}):
        from utils import sync as sy          # lazy: sync imports this module
        await sy.push_now(client)
    await apply_milestone(client, by, total, settings)
    return True


async def apply_remote_event(client, d, settings):
    """A referral that happened in the partner bot."""
    if not settings.get('ref_enabled', True):
        return
    inserted, total = await db.record_referral(d['u'], d['by'], d.get('wk'), d.get('ts'))
    if inserted:
        await apply_milestone(client, d['by'], total, settings)


async def on_first_file(client, user_id):
    """The user received a file: if they were referred, their referral becomes 'active' (counts for the weekly race)."""
    if not await db.mark_got_file(user_id):
        return
    if await db.qualify_referral(user_id):
        if await db.sync_queue_event(f"rq_{user_id}", {'kind': 'refq', 'u': user_id}):
            from utils import sync as sy
            await sy.push_now(client)


# ---------------- screen ----------------
def prizes_text(settings):
    prizes = settings.get('ref_weekly') or [10, 8, 6, 4, 2]
    return " ".join(f"{MEDALS[i]}{d}d" for i, d in enumerate(prizes[:5]))


async def refer_view(client, user_id, lang, settings):
    me = getattr(client.me, 'username', None)
    if not settings.get('ref_enabled', True) or not me:
        return tr(lang, 'ref_off'), kb([[btn(tr(lang, 'b_back'), 'u:home')]])
    need = max(int(settings.get('ref_need', 5) or 5), 1)
    total = await db.ref_total(user_id)
    filled = total % need
    segs = round(filled / need * 10)
    bar = '▰' * segs + '▱' * (10 - segs)
    wk = week_key()
    top = await db.ref_top(wk, 5)
    rank = await db.ref_week_rank(user_id, wk)
    lines = []
    for i, (uid, n) in enumerate(top):
        lines.append(f"{MEDALS[i]} {html.escape(await db.display_name(uid))} · {n}")
    link = ref_link(me, user_id)
    text = tr(lang, 'ref_screen', need=need, days=int(settings.get('ref_days', 1) or 1), count=total, left=need - filled, bar=bar,
              earned=await db.ref_days_earned(user_id), rank=f"#{rank}" if rank else "—",
              top="\n".join(lines) if lines else tr(lang, 'ref_none'), prizes=prizes_text(settings), link=link)
    rows = [[btn(tr(lang, 'b_share_link'), url=share_url(link, tr(lang, 'ref_share_text')))],
            [btn(tr(lang, 'b_back'), 'u:home')]]
    rows.extend(more_row(settings, lang))
    return text, kb(rows)


# ---------------- weekly prizes ----------------
async def award_weekly(client, settings=None):
    """After Monday 00:10 IST, give the previous week's top 5 their bonus days (once)."""
    s = settings or await db.get_settings()
    if not s.get('ref_enabled', True):
        return 0
    now = int(time.time())
    cur_start = week_start_ts(now)
    if now < cur_start + 600:
        return 0
    prev = week_key(cur_start - 86400)
    mark = f"wk_done_{prev}"
    if await db.ref_rewards.find_one({'_id': mark}):
        return 0
    prizes = s.get('ref_weekly') or [10, 8, 6, 4, 2]
    given = 0
    for rank, (uid, n) in enumerate(await db.ref_top(prev, 5), 1):
        days = int(prizes[rank - 1]) if rank - 1 < len(prizes) else 0
        if days <= 0:
            continue
        if await db.claim_reward(f"w_{prev}_{rank}_{uid}", uid, days, 'weekly'):
            exp = await db.extend_premium(uid, days)
            given += 1
            print(f"🏆 Weekly prize: #{rank} {uid} +{days} day(s)")
            await notify(client, uid, 'ref_week_prize', rank=rank, n=n, days=days, date=ist_str(exp))
    await db.claim_reward(mark, 0, 0, 'mark')
    return given


async def referral_loop(client):
    await asyncio.sleep(60)
    while True:
        try:
            await award_weekly(client)
        except Exception as e:
            print(f"Referral loop error: {e}")
        await asyncio.sleep(600)
