import os


def _clean(v: str) -> str:
    return v.strip().lstrip("﻿") if v else v


BOT_TOKEN = _clean(os.getenv("BOT_TOKEN", "8411386595:AAG_WffgEJ0ihe7gJZyifNexBZ1i0tHfPWg"))
CHANNEL_ID = _clean(os.getenv("CHANNEL_ID", "@tezkorofficial_uz"))
OWNER_ID = int(_clean(os.getenv("OWNER_ID", "679291909")))

FOOTER = "➖ Bizga obuna bo'ling: @tezkorofficial_uz"

MIN_INTERVAL_SEC = int(os.getenv("MIN_INTERVAL_SEC", 2 * 60))
MAX_INTERVAL_SEC = int(os.getenv("MAX_INTERVAL_SEC", 4 * 60))

DB_PATH = os.getenv("DB_PATH", "posted.db")

TELEGRAM_CHANNELS = ["aniquz", "Geointriga_uz"]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
