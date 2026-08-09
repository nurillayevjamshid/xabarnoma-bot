import sqlite3
import hashlib
from contextlib import contextmanager
from config import DB_PATH


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
    # This makes the hash resistant to minor spacing or punctuation changes
    normalized = "".join(ch.lower() for ch in t if ch.isalnum())
    # Take only first 100 chars to avoid hash collisions on very long titles 
    # but still keep it unique enough
    return hashlib.md5(normalized[:200].encode("utf-8")).hexdigest()


def is_posted(url: str, title: str) -> bool:
    with _conn() as c:
        cur = c.execute(
            "SELECT 1 FROM posted WHERE url = ? OR title_hash = ? LIMIT 1",
            (url, _norm_title(title)),
        )
        return cur.fetchone() is not None


def mark_posted(url: str, title: str):
    with _conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO posted (url, title_hash) VALUES (?, ?)",
            (url, _norm_title(title)),
        )


def cleanup_old(days: int = 30) -> int:
    with _conn() as c:
        cur = c.execute(
            "DELETE FROM posted WHERE created_at < datetime('now', ?)",
            (f'-{days} days',),
        )
        return cur.rowcount
