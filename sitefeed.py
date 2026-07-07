import json
import logging
import os
import re

log = logging.getLogger("xabarnoma")

POSTS_PATH = os.getenv("SITE_POSTS_PATH", "docs/posts.json")
MAX_POSTS = 300  # saytda saqlanadigan eng ko'p post soni

_channel_re = re.compile(r"t\.me/([^/]+)/")


def append_post(article) -> None:
    """Telegramga yuborilgan postni sayt lentasiga (docs/posts.json) qo'shadi.
    Xato bo'lsa botni to'xtatmaydi — sayt ikkilamchi kanal."""
    try:
        posts = []
        if os.path.exists(POSTS_PATH):
            with open(POSTS_PATH, encoding="utf-8") as f:
                posts = json.load(f)
        if any(p.get("url") == article.url for p in posts):
            return
        m = _channel_re.search(article.url)
        posts.insert(0, {
            "url": article.url,
            "title": article.title,
            "body": article.body,
            "image": article.image_url,
            "video": article.video_url,
            "published": article.published,
            "channel": m.group(1) if m else "",
        })
        del posts[MAX_POSTS:]
        os.makedirs(os.path.dirname(POSTS_PATH), exist_ok=True)
        with open(POSTS_PATH, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, separators=(",", ":"))
    except Exception as e:
        log.warning(f"Sayt lentasiga yozilmadi: {e}")
