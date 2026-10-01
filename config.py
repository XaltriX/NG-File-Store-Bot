import os
from dotenv import load_dotenv

load_dotenv()

# ==============================================================================
#  FILL YOUR VALUES BELOW (between the quotes / after the = sign).
#  You can also use a .env file or hosting environment variables instead:
#  a value from the environment, if present, overrides the one written here.
# ==============================================================================


def _get(name, default=""):
    value = os.environ.get(name)
    return default if value is None or str(value).strip() == "" else value


def _int(name, default=0):
    try:
        return int(str(_get(name, default)).strip())
    except ValueError:
        return default


class Config:
    # ---------- REQUIRED ----------
    API_ID = _int("API_ID", 0)                               # from my.telegram.org
    API_HASH = _get("API_HASH", "")                          # from my.telegram.org
    BOT_TOKEN = _get("BOT_TOKEN", "")                        # from @BotFather (use the SAME token as your old bot)
    OWNER_ID = _int("OWNER_ID", 0)                           # YOUR numeric Telegram ID (get it from @userinfobot)
    MONGO_URI_1 = _get("MONGO_URI_1", "")                    # MongoDB connection URL
    MONGO_DB_NAME = _get("MONGO_DB_NAME", "filestorebot")    # same name as your old DB if you reuse it
    DB_CHANNEL = _int("DB_CHANNEL", 0)                       # the channel that holds your files, like -1001234567890

    # ---------- OPTIONAL ----------
    LOG_CHANNEL = _int("LOG_CHANNEL", 0)                     # new-user logs go here (leave 0 to disable)
    MONGO_URI_2 = _get("MONGO_URI_2", "")                    # extra MongoDB for more storage
    MONGO_URI_3 = _get("MONGO_URI_3", "")
    FSUB_CHANNELS = _get("FSUB_CHANNELS", "")

    # Buttons shown to users (leave empty to hide a button)
    SUPPORT_LINK = _get("SUPPORT_LINK", "")                  # e.g. https://t.me/your_support
    UPDATES_LINK = _get("UPDATES_LINK", "")                  # e.g. https://t.me/your_channel
    MOVIES_LINK = _get("MOVIES_LINK", "")
    SERIES_LINK = _get("SERIES_LINK", "")
    DEVELOPER_LINK = _get("DEVELOPER_LINK", "")
    OWNER_LINK = _get("OWNER_LINK", "")
    PREMIUM_LINK = _get("PREMIUM_LINK", "")

    # Shortner defaults (you can also set these later from the Admin Panel)
    SHORTENER_URL = _get("SHORTENER_URL", "")
    SHORTENER_API = _get("SHORTENER_API", "")
    TUTORIAL_LINK = _get("TUTORIAL_LINK", "")
    VERIFY_EXPIRE = _int("VERIFY_EXPIRE", 86400)

    # Pictures (direct image links). Replace with your own if you like.
    VERIFY_IMG = _get("VERIFY_IMG", "https://i.ibb.co/XkWwHqy8/photo-2026-09-04-23-47-45-7681831085168132132.jpg")
    START_PIC = _get("START_PIC", "https://i.ibb.co/DPbqZ7Mn/photo-2026-09-04-23-38-51-7681830930549309480.jpg")

    # Text shown under every delivered file, e.g. "Powered by @YourChannel" (empty = nothing)
    BRANDING_TEXT = _get("BRANDING_TEXT", "")

    # Only if you run your OWN Cloudflare worker for Web Guard (otherwise leave empty = off)
    GUARD_URL = _get("GUARD_URL", "")
    GUARD_SECRET = _get("GUARD_SECRET", "")

    # Only if your old bot used a DIFFERENT file channel than DB_CHANNEL (normally leave 0)
    OLD_DB_CHANNEL = _int("OLD_DB_CHANNEL", 0)


# ---------- startup check: tells you exactly what is still empty ----------
_missing = [name for name, ok in (
    ("API_ID", Config.API_ID > 0),
    ("API_HASH", bool(Config.API_HASH)),
    ("BOT_TOKEN", bool(Config.BOT_TOKEN)),
    ("OWNER_ID", Config.OWNER_ID > 0),
    ("MONGO_URI_1", bool(Config.MONGO_URI_1)),
    ("DB_CHANNEL", Config.DB_CHANNEL != 0),
) if not ok]

if _missing:
    raise SystemExit(
        "\n[CONFIG ERROR] Please fill these in config.py (or .env): " + ", ".join(_missing) + "\n"
        "Tip: OWNER_ID is YOUR Telegram user ID (get it from @userinfobot).\n"
    )
