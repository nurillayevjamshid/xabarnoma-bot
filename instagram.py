import asyncio
import logging
import os
import tempfile
from functools import partial
from pathlib import Path
import aiohttp
from config import IG_USERNAME, IG_PASSWORD, IG_SESSION_FILE, IG_FOOTER
from scraper import Article
from publisher import _first_paragraph

log = logging.getLogger("xabarnoma")

CAPTION_LIMIT = 2200
_client = None


def _get_client():
    """instagrapi Client — session fayli bo'lsa qayta login qilmaydi."""
    global _client
    if _client is not None:
        return _client

    from instagrapi import Client
    cl = Client()
    cl.delay_range = [2, 5]  # so'rovlar orasida tasodifiy pauza (soniya)

    if Path(IG_SESSION_FILE).exists():
        try:
            cl.load_settings(IG_SESSION_FILE)
            cl.login(IG_USERNAME, IG_PASSWORD)
            log.info("Instagram: session faylidan kirilib olindi")
            _client = cl
            return _client
        except Exception as e:
            log.warning(f"Instagram session eskirgan, qayta login: {e}")

    cl.login(IG_USERNAME, IG_PASSWORD)
    cl.dump_settings(IG_SESSION_FILE)
    log.info("Instagram: yangi login muvaffaqiyatli")
    _client = cl
    return _client


def _build_caption(article: Article) -> str:
    title = article.title.strip()
    summary = _first_paragraph(article.body)
    footer = IG_FOOTER.strip()

    head = f"{title}\n\n"
    tail = f"\n\n{footer}" if footer else ""
    available = CAPTION_LIMIT - len(head) - len(tail) - 5

    if len(summary) > available:
        summary = summary[:available].rsplit(" ", 1)[0] + "..."

    return f"{head}{summary}{tail}"


async def _download_image(image_url: str) -> str | None:
    """Rasmni vaqtinchalik faylga yuklab oladi va uning yo'lini qaytaradi."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=30) as resp:
                if resp.status != 200:
                    return None
                data = await resp.read()
        suffix = ".jpg"
        if "png" in image_url.lower():
            suffix = ".png"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(data)
        tmp.close()
        return tmp.name
    except Exception as e:
        log.warning(f"Rasm yuklab olinmadi: {e}")
        return None


async def publish(article: Article) -> bool:
    """Maqolani Instagramga joylaydi. Rasmsiz maqolalar o'tkazib yuboriladi."""
    if not article.image_url:
        return False
    if not (IG_USERNAME and IG_PASSWORD):
        log.warning("Instagram sozlanmagan (username yoki password yo'q)")
        return False

    img_path = await _download_image(article.image_url)
    if not img_path:
        return False

    caption = _build_caption(article)

    loop = asyncio.get_event_loop()
    try:
        def _upload():
            cl = _get_client()
            cl.photo_upload(img_path, caption)

        await loop.run_in_executor(None, _upload)
        log.info(f"Instagram: post yuborildi — {article.title[:60]}")
        return True
    except Exception as e:
        log.error(f"Instagram post xatosi: {e}")
        # Session muammosi bo'lsa, keyingi urinishda yangi login qilinadi.
        global _client
        _client = None
        return False
    finally:
        try:
            os.unlink(img_path)
        except OSError:
            pass
