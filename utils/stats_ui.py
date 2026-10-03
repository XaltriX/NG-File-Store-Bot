import time
from datetime import timedelta
from config import Config
from utils.database import db

BOT_START = time.time()


async def build_stats_text():
    total_users = await db.total_users()
    total_files = await db.total_files()
    total_banned = await db.total_banned_users()
    settings = await db.get_settings()
    counts = await db.verify_counts()
    p_now, p_ever = await db.premium_stats()
    v_now, v_ever = await db.verified_stats(settings.get('shortlink_type') == 'credit')
    today_s = await db.get_day_stats(0)
    uptime = str(timedelta(seconds=int(time.time() - BOT_START)))

    def line(label, d):
        per = " | ".join(f"S{n}: {c}" for n, c in d['s'].items())
        return f"{label}: <b>{d['total']}</b>  ({per})"

    sl = "ON" if settings.get('shortlink_status') else "OFF"
    sl_type = str(settings.get('shortlink_type', 'time')).capitalize()
    dual = "ON" if settings.get('dual_shortner') else "OFF"
    guard = "ON" if settings.get('web_guard') else "OFF"
    multi = "Active" if Config.MONGO_URI_2 else "Inactive"

    return (
        "📊 <b>Bot Statistics</b>\n\n"
        "<blockquote>"
        f"✅ {line('Verified today', counts['today'])}\n"
        f"🕘 {line('Yesterday', counts['yesterday'])}"
        "</blockquote>\n"
        "<blockquote>"
        f"💎 Premium now: <b>{p_now:,}</b> · ever: <b>{p_ever:,}</b>\n"
        f"✅ Verified now: <b>{v_now:,}</b> · ever (unique): <b>{v_ever:,}</b>"
        "</blockquote>\n"
        "<blockquote>"
        f"🎁 Trials started today: <b>{today_s.get('trials_started', 0)}</b>\n"
        f"⏰ Reminders sent today: <b>{today_s.get('reminders_sent', 0)}</b>\n"
        f"👆 Reminder clicks today: <b>{today_s.get('reminder_clicks', 0)}</b>\n"
        f"✅ Verified via reminder: <b>{today_s.get('reminder_verifies', 0)}</b>\n"
        f"💎 Premium approved today: <b>{today_s.get('prem_approved', 0)}</b>"
        "</blockquote>\n"
        "<blockquote>"
        f"👥 Users: <b>{total_users}</b>   🚫 Banned: <b>{total_banned}</b>\n"
        f"📁 Files: <b>{total_files}</b>   🗄 Multi-DB: <b>{multi}</b>\n"
        f"🔗 Shortlink: <b>{sl} ({sl_type})</b>   Dual: <b>{dual}</b>\n"
        f"🛡 Web guard: <b>{guard}</b>\n"
        f"⏱ Uptime: <code>{uptime}</code>"
        "</blockquote>\n"
        "<i>Verified counts are unique users per IST day. Older data is removed automatically.</i>"
    )
