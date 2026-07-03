import os


def _clean(v: str) -> str:
    return v.strip().lstrip("﻿") if v else v


BOT_TOKEN = _clean(os.getenv("BOT_TOKEN", "8411386595:AAG_WffgEJ0ihe7gJZyifNexBZ1i0tHfPWg"))
CHANNEL_ID = _clean(os.getenv("CHANNEL_ID", "@xabarnomaofficial"))
OWNER_ID = int(_clean(os.getenv("OWNER_ID", "679291909")))

FOOTER = "➖ Bizga obuna bo'ling: @xabarnomaofficial"

MIN_INTERVAL_SEC = int(os.getenv("MIN_INTERVAL_SEC", 2 * 60))
MAX_INTERVAL_SEC = int(os.getenv("MAX_INTERVAL_SEC", 4 * 60))

DB_PATH = os.getenv("DB_PATH", "posted.db")

TELEGRAM_CHANNELS = ["aniquz", "Geointriga_uz"]

# --- Instagram (instagrapi orqali) ---
# Yoqish uchun IG_ENABLED=1, IG_USERNAME va IG_PASSWORD ni o'rnating.
IG_ENABLED = _clean(os.getenv("IG_ENABLED", "")).lower() in ("1", "true", "yes")
IG_USERNAME = _clean(os.getenv("IG_USERNAME", ""))
IG_PASSWORD = _clean(os.getenv("IG_PASSWORD", ""))
# Session faylini saqlash joyi (qayta login qilishni kamaytiradi).
IG_SESSION_FILE = _clean(os.getenv("IG_SESSION_FILE", "ig_session.json"))
# Instagram ancha sekinroq post qiladi (kuniga 20-25 dan oshirmaslik kerak).
IG_MIN_INTERVAL_SEC = int(os.getenv("IG_MIN_INTERVAL_SEC", 60 * 60))   # 1 soat
IG_MAX_INTERVAL_SEC = int(os.getenv("IG_MAX_INTERVAL_SEC", 90 * 60))   # 1.5 soat
IG_DAILY_LIMIT = int(os.getenv("IG_DAILY_LIMIT", 20))
# Instagram caption oxiriga qo'shiladigan matn.
IG_FOOTER = _clean(os.getenv("IG_FOOTER", "Telegram: @xabarnomaofficial"))

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
