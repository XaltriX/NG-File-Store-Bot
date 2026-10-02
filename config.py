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
    API_ID = _int("API_ID", 24955235)                               # from my.telegram.org
    API_HASH = _get("API_HASH", "f317b3f7bbe390346d8b46868cff0de8")                          # from my.telegram.org
    BOT_TOKEN = _get("BOT_TOKEN", "")                        # from @BotFather (use the SAME token as your old bot)
    OWNER_ID = _int("OWNER_ID", 5706788169)                           # YOUR numeric Telegram ID (get it from @userinfobot)
    MONGO_URI_1 = _get("MONGO_URI_1", "mongodb+srv://teddugovardhan544_db_user:WVjIA96jQ31net0j@cluster0.kwkkleo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")                    # MongoDB connection URL
    MONGO_DB_NAME = _get("MONGO_DB_NAME", "nightrider")    # same name as your old DB if you reuse it
    DB_CHANNEL = _int("DB_CHANNEL", -1002004278204)                       # the channel that holds your files, like -1001234567890

    # ---------- OPTIONAL ----------
    LOG_CHANNEL = _int("LOG_CHANNEL", -1004317336836)                     # new-user logs go here (leave 0 to disable)
    MONGO_URI_2 = _get("MONGO_URI_2", "")                    # extra MongoDB for more storage
    MONGO_URI_3 = _get("MONGO_URI_3", "")
    FSUB_CHANNELS = _get("FSUB_CHANNELS", "")

    # Buttons shown to users (leave empty to hide a button)
    SUPPORT_LINK = _get("SUPPORT_LINK", "https://t.me/+_wyXYGQV6Nw3NDA1")                  # e.g. https://t.me/your_support
    UPDATES_LINK = _get("UPDATES_LINK", "https://t.me/+eU9PSVk0ohg2M2U0")                  # e.g. https://t.me/your_channel
    MOVIES_LINK = _get("MOVIES_LINK", "https://t.me/+p2dAkUL0d2NhYTM9")
    SERIES_LINK = _get("SERIES_LINK", "https://t.me/+p2dAkUL0d2NhYTM9")
    DEVELOPER_LINK = _get("DEVELOPER_LINK", "https://t.me/NeonGhost")
    OWNER_LINK = _get("OWNER_LINK", "https://t.me/NeonGhost")
    PREMIUM_LINK = _get("PREMIUM_LINK", "")

    # Shortner defaults (you can also set these later from the Admin Panel)
    SHORTENER_URL = _get("SHORTENER_URL", "")
    SHORTENER_API = _get("SHORTENER_API", "")
    TUTORIAL_LINK = _get("TUTORIAL_LINK", "")
    VERIFY_EXPIRE = _int("VERIFY_EXPIRE", 86400)

    # Pictures (direct image links). Replace with your own if you like.
    VERIFY_IMG = _get("VERIFY_IMG", "https://files.catbox.moe/t0gn23.jpg")
    START_PIC = _get("START_PIC", "https://files.catbox.moe/ybhkr0.jpg")

    # Text shown under every delivered file, e.g. "Powered by @YourChannel" (empty = nothing)
    BRANDING_TEXT = _get("BRANDING_TEXT", "@linkz_Wallah")

    # Only if you run your OWN Cloudflare worker for Web Guard (otherwise leave empty = off)
    GUARD_URL = _get("GUARD_URL", "https://luxeguard.souravbosu947.workers.dev")
    GUARD_SECRET = _get("GUARD_SECRET", "Luxe_Super_Secret_Guard_2026")

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
