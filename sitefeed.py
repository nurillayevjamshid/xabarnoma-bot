import hashlib
import json
import logging
import os
import re
import urllib.request

log = logging.getLogger("xabarnoma")

POSTS_PATH = os.getenv("SITE_POSTS_PATH", "docs/posts.json")
IMG_DIR = os.getenv("SITE_IMG_DIR", "docs/img")
RAW_BASE = "https://raw.githubusercontent.com/nurillayevjamshid/xabarnoma-bot/main/docs/img/"
MAX_POSTS = 300  # saytda saqlanadigan eng ko'p post soni
MAX_IMG_BYTES = 5 * 1024 * 1024

_channel_re = re.compile(r"t\.me/([^/]+)/")


def _save_image(url: str) -> str:
    """Rasmni repoga (docs/img) yuklab oladi va doimiy havolasini qaytaradi.
    Shunda sayt Telegram CDN'ga bog'liq bo'lmaydi — rasm doim ochiladi."""
    name = hashlib.md5(url.encode()).hexdigest()[:16] + ".jpg"
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read(MAX_IMG_BYTES + 1)
        if not data or len(data) > MAX_IMG_BYTES:
            raise ValueError("rasm hajmi mos emas")
        os.makedirs(IMG_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    return RAW_BASE + name


def _drop_image(image_url: str) -> None:
    if image_url and image_url.startswith(RAW_BASE):
        try:
            os.remove(os.path.join(IMG_DIR, image_url.rsplit("/", 1)[-1]))
        except OSError:
            pass


def migrate_images() -> None:
    """Lentadagi tashqi (Telegram CDN) rasm havolalarini repoga ko'chiradi.
    Telegram CDN ba'zi provayderlarda ochilmaydi — repodagi nusxa doim ishlaydi."""
    try:
        if not os.path.exists(POSTS_PATH):
            return
        with open(POSTS_PATH, encoding="utf-8") as f:
            posts = json.load(f)
        changed = False
        for p in posts:
            img = p.get("image") or ""
            if img and not img.startswith(RAW_BASE):
                try:
                    p["image"] = _save_image(img)
                    changed = True
                except Exception as e:
                    log.warning(f"Migratsiya: rasm olinmadi: {e}")
        if changed:
            with open(POSTS_PATH, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, separators=(",", ":"))
            log.info("Sayt rasmlari repoga ko'chirildi")
    except Exception as e:
        log.warning(f"Rasm migratsiyasi xatosi: {e}")


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

        image = article.image_url
        if image:
            try:
                image = _save_image(image)
            except Exception as e:
                log.warning(f"Rasm saqlanmadi, asl havola ishlatiladi: {e}")

        m = _channel_re.search(article.url)
        posts.insert(0, {
            "url": article.url,
            "title": article.title,
            "body": article.body,
            "image": image,
            "video": article.video_url,
            "published": article.published,
            "channel": m.group(1) if m else "",
        })
        for old in posts[MAX_POSTS:]:
            _drop_image(old.get("image") or "")
        del posts[MAX_POSTS:]

        os.makedirs(os.path.dirname(POSTS_PATH), exist_ok=True)
        with open(POSTS_PATH, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, separators=(",", ":"))
    except Exception as e:
        log.warning(f"Sayt lentasiga yozilmadi: {e}")
