"""Posts the payment screenshot + a 'New Premium Member' caption to the proof channel."""
import html
from pyrogram.enums import ParseMode
from pyrogram.types import LinkPreviewOptions
from utils.i18n import PROOF_CAPTION
from utils.prem import owner_url, sync_active
from utils.ui import btn, kb


def render_proof(settings, name, plan, me):
    tpl = settings.get('proof_caption') or PROOF_CAPTION
    partner = (settings.get('partner_username') or '').lstrip('@')
    if me and partner and sync_active(settings):
        bots = f"@{me} · @{partner}"
    else:
        bots = f"@{me}" if me else ""
    return (tpl.replace('{name}', html.escape(name or 'Member'))
               .replace('{plan}', html.escape(plan.get('name', '')))
               .replace('{days}', str(plan.get('days', '')))
               .replace('{bots}', html.escape(bots)))


def proof_markup(settings, me):
    row = []
    if me:
        row.append(btn("💎 Buy Premium", url=f"https://t.me/{me}?start=premium"))
    contact = owner_url(settings)
    if contact:
        row.append(btn("💬 Contact", url=contact))
    return kb([row]) if row else None


async def post_proof(client, settings, pay, plan):
    """Returns (ok, error_text). Never raises, so a failed post can not block a premium approval."""
    chat = int(settings.get('proof_chat') or 0)
    if not chat:
        return False, "proof channel not set"
    me = getattr(client.me, 'username', None)
    caption = render_proof(settings, pay.get('name'), plan, me)
    markup = proof_markup(settings, me)
    fid, ftype = pay.get('fid'), pay.get('ftype')
    try:
        if fid and ftype == 'photo':
            await client.send_photo(chat, fid, caption=caption, reply_markup=markup, parse_mode=ParseMode.HTML)
        elif fid:
            await client.send_document(chat, fid, caption=caption, reply_markup=markup, parse_mode=ParseMode.HTML)
        else:
            await client.send_message(chat, caption, reply_markup=markup, parse_mode=ParseMode.HTML,
                                      link_preview_options=LinkPreviewOptions(is_disabled=True))
        return True, ""
    except Exception as e:
        return False, type(e).__name__
