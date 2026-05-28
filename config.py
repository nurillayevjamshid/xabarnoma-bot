import os


def _clean(v: str) -> str:
    return v.strip().lstrip("﻿") if v else v


BOT_TOKEN = _clean(os.getenv("BOT_TOKEN", "8411386595:AAG_WffgEJ0ihe7gJZyifNexBZ1i0tHfPWg"))
CHANNEL_ID = _clean(os.getenv("CHANNEL_ID", "@xabarnomaofficial"))
OWNER_ID = int(_clean(os.getenv("OWNER_ID", "679291909")))

FOOTER = "\n\nBizni kuzatib boring https://www.instagram.com/xabarnomauz/"

MIN_INTERVAL_SEC = 5 * 60
MAX_INTERVAL_SEC = 10 * 60

DB_PATH = os.getenv("DB_PATH", "posted.db")

SOURCES = ["kun.uz", "qalampir.uz", "aniq.uz"]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
