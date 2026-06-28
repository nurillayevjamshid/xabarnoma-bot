import sqlite3
import hashlib
from contextlib import contextmanager
from config import DB_PATH

# Har bir platforma uchun alohida jadval. Shu tariqa bitta maqola
# Telegramga yuborilgan bo'lsa-da, Instagramga hali yuborilmagan bo'lishi mumkin.
TABLES = ("posted", "posted_ig")


def init_db():
    with _conn() as c:
        for table in TABLES:
            c.execute(
                f"""CREATE TABLE IF NOT EXISTS {table} (
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


def _check_table(table: str) -> str:
    if table not in TABLES:
        raise ValueError(f"Noma'lum jadval: {table}")
    return table


def _norm_title(t: str) -> str:
    return hashlib.md5(
        "".join(ch.lower() for ch in t if ch.isalnum()).encode("utf-8")
    ).hexdigest()


def is_posted(url: str, title: str, table: str = "posted") -> bool:
    _check_table(table)
    with _conn() as c:
        cur = c.execute(
            f"SELECT 1 FROM {table} WHERE url = ? OR title_hash = ? LIMIT 1",
            (url, _norm_title(title)),
        )
        return cur.fetchone() is not None


def mark_posted(url: str, title: str, table: str = "posted"):
    _check_table(table)
    with _conn() as c:
        c.execute(
            f"INSERT OR IGNORE INTO {table} (url, title_hash) VALUES (?, ?)",
            (url, _norm_title(title)),
        )


def count_recent(hours: int, table: str = "posted") -> int:
    """Oxirgi `hours` soat ichida yuborilgan yozuvlar soni."""
    _check_table(table)
    with _conn() as c:
        cur = c.execute(
            f"SELECT COUNT(*) FROM {table} WHERE created_at > datetime('now', ?)",
            (f"-{hours} hours",),
        )
        return cur.fetchone()[0]


def cleanup_old(days: int = 30, table: str = "posted") -> int:
    _check_table(table)
    with _conn() as c:
        cur = c.execute(
            f"DELETE FROM {table} WHERE created_at < datetime('now', ?)",
            (f'-{days} days',),
        )
        return cur.rowcount
