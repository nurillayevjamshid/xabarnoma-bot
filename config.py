import os


def _clean(v: str) -> str:
    return v.strip().lstrip("") if v else v


BOT_TOKEN = _clean(os.getenv("BOT_TOKEN", "8224265387:AAHM2D9-lcedRnkfFsLc1Xoru-Uo2MFcIYA"))
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN secret is required")
CHANNEL_ID = _clean(os.getenv("CHANNEL_ID", "@tezkorofficial_uz"))
OWNER_ID = int(_clean(os.getenv("OWNER_ID", "679291909")))

FOOTER = """Yangilikni yaqinlarga ham ulashing
📸 <a href="https://www.instagram.com/tezkor.official/">Instagram</a>  ▶️ <a href="https://www.youtube.com/@tezkor.official">YouTube</a>"""

MIN_INTERVAL_SEC = int(os.getenv("MIN_INTERVAL_SEC", 2 * 60))
MAX_INTERVAL_SEC = int(os.getenv("MAX_INTERVAL_SEC", 4 * 60))

# On Vercel, the filesystem is read-only except for /tmp
if os.getenv("VERCEL"):
    DB_PATH = "/tmp/posted.db"
else:
    DB_PATH = os.getenv("DB_PATH", "posted.db")

TELEGRAM_CHANNELS = ["uz24newsuz"]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
