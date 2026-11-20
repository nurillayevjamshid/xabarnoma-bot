import sqlite3
import hashlib
import json
import os
import re
from contextlib import contextmanager
from config import DB_PATH

POSTS_JSON_PATH = os.getenv("SITE_POSTS_PATH", "docs/posts.json")
POSTED_URLS_TXT = "docs/posted_urls.txt"


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
            (f'-{days} days',),
        )
        return cur.rowcount
