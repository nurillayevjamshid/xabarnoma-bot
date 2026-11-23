import sqlite3
import hashlib
import json
import os
import re
import time
import ssl
import urllib.request
from contextlib import contextmanager
from bs4 import BeautifulSoup
from config import DB_PATH, CHANNEL_ID
from translit import to_latin

POSTS_JSON_PATH = os.getenv("SITE_POSTS_PATH", "docs/posts.json")
POSTED_URLS_TXT = "docs/posted_urls.txt"

_CHANNEL_CACHE_TIME = 0.0
_CHANNEL_CACHE_TEXTS: list[str] = []


def init_db():
    with _conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS posted (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title_hash TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _norm_title(t: str) -> str:
    # Remove all whitespace, special characters, and convert to lower
    normalized = "".join(ch.lower() for ch in t if ch.isalnum())
    return hashlib.md5(normalized[:200].encode("utf-8")).hexdigest()


def _norm_for_channel_match(t: str) -> str:
    if not t:
        return ""
    try:
        latin = to_latin(t).lower()
    except Exception:
        latin = t.lower()
    latin = latin.replace("ç", "ch").replace("ş", "sh").replace("ō", "o").replace("ğ", "g")
    latin = latin.replace("ʻ", "").replace("ʼ", "").replace("'", "").replace("`", "")
    return "".join(ch for ch in latin if ch.isalnum())


def get_channel_recent_texts(channel: str = None, force_refresh: bool = False) -> list[str]:
    global _CHANNEL_CACHE_TIME, _CHANNEL_CACHE_TEXTS
    now = time.monotonic()
    if not force_refresh and (now - _CHANNEL_CACHE_TIME < 60.0) and _CHANNEL_CACHE_TEXTS:
        return _CHANNEL_CACHE_TEXTS

    ch = (channel or CHANNEL_ID or "tezkorofficial_uz").lstrip("@").strip()
    try:
        url = f"https://t.me/s/{ch}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
            html = r.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        texts = []
        for p in soup.select(".tgme_widget_message_text"):
            t = _norm_for_channel_match(p.get_text())
            if t:
                texts.append(t)
        if texts:
            _CHANNEL_CACHE_TEXTS = texts
            _CHANNEL_CACHE_TIME = now
    except Exception:
        pass
    return _CHANNEL_CACHE_TEXTS


def is_in_telegram_channel(title: str, channel: str = None, force_refresh: bool = False) -> bool:
    if not title:
        return False
    needle = _norm_for_channel_match(title)[:35]
    if len(needle) < 10:
        return False
    texts = get_channel_recent_texts(channel, force_refresh=force_refresh)
    return any(needle in t for t in texts)


def is_posted(url: str, title: str) -> bool:
    # 1. Check SQLite posted.db
    try:
        with _conn() as c:
            cur = c.execute(
                "SELECT 1 FROM posted WHERE url = ? OR title_hash = ? LIMIT 1",
                (url, _norm_title(title)),
            )
            if cur.fetchone() is not None:
                return True
    except Exception:
        pass

    # 2. Check plain-text posted_urls.txt (git-safe fallback)
    try:
        if os.path.exists(POSTED_URLS_TXT):
            with open(POSTED_URLS_TXT, "r", encoding="utf-8") as f:
                urls = {line.strip() for line in f if line.strip()}
                if url.strip() in urls:
                    return True
    except Exception:
        pass

    # 3. Check docs/posts.json
    try:
        if os.path.exists(POSTS_JSON_PATH):
            with open(POSTS_JSON_PATH, "r", encoding="utf-8") as f:
                posts = json.load(f)
                target_hash = _norm_title(title)
                for p in posts:
                    if p.get("url") == url:
                        return True
                    if p.get("title") and _norm_title(p["title"]) == target_hash:
                        return True
    except Exception:
        pass

    # 4. Check Telegram Channel Live Feed (Live Anti-Duplicate Guard)
    try:
        if is_in_telegram_channel(title):
            # Already visible in the channel. Mark locally so subsequent checks are instant.
            mark_posted(url, title)
            return True
    except Exception:
        pass

    return False


def mark_posted(url: str, title: str):
    # 1. Save to SQLite
    try:
        with _conn() as c:
            c.execute(
                "INSERT OR IGNORE INTO posted (url, title_hash) VALUES (?, ?)",
                (url, _norm_title(title)),
            )
    except Exception:
        pass

    # 2. Append to plain-text posted_urls.txt
    try:
        os.makedirs(os.path.dirname(POSTED_URLS_TXT) or ".", exist_ok=True)
        with open(POSTED_URLS_TXT, "a", encoding="utf-8") as f:
            f.write(f"{url.strip()}\n")
    except Exception:
        pass


def cleanup_old(days: int = 30) -> int:
    with _conn() as c:
        cur = c.execute(
            "DELETE FROM posted WHERE created_at < datetime('now', ?)",
            (f"-{days} days",),
        )
        return cur.rowcount
