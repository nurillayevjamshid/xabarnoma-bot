import asyncio
import logging
import aiohttp
from config import IG_ACCESS_TOKEN, IG_USER_ID, IG_GRAPH_VERSION, IG_FOOTER
from scraper import Article
from publisher import _first_paragraph

log = logging.getLogger("xabarnoma")

# Instagram caption limiti 2200 belgi.
CAPTION_LIMIT = 2200
GRAPH_BASE = f"https://graph.facebook.com/{IG_GRAPH_VERSION}"


def _build_caption(article: Article) -> str:
    """Instagram caption — oddiy matn (HTML emas)."""
    title = article.title.strip()
    summary = _first_paragraph(article.body)
    footer = IG_FOOTER.strip()

    head = f"{title}\n\n"
    tail = f"\n\n{footer}" if footer else ""
    available = CAPTION_LIMIT - len(head) - len(tail) - 5

    if len(summary) > available:
        summary = summary[:available].rsplit(" ", 1)[0] + "..."

    return f"{head}{summary}{tail}"


async def _post(session: aiohttp.ClientSession, url: str, data: dict) -> dict:
    async with session.post(url, data=data, timeout=60) as resp:
        try:
            payload = await resp.json()
        except Exception:
            payload = {"_raw": await resp.text()}
        if resp.status != 200:
            log.error(f"Instagram API xatosi ({resp.status}): {payload}")
        return payload


async def _wait_ready(session: aiohttp.ClientSession, creation_id: str) -> bool:
    """Media konteyner tayyor bo'lishini kutadi (rasm uchun odatda darhol)."""
    status_url = f"{GRAPH_BASE}/{creation_id}"
    params = {"fields": "status_code", "access_token": IG_ACCESS_TOKEN}
    for _ in range(10):
        async with session.get(status_url, params=params, timeout=60) as resp:
            data = await resp.json()
        code = data.get("status_code")
        if code == "FINISHED":
            return True
        if code == "ERROR":
            log.error(f"Instagram konteyner xatosi: {data}")
            return False
        await asyncio.sleep(3)
    log.warning("Instagram konteyner vaqtida tayyor bo'lmadi")
    return False


async def publish(session: aiohttp.ClientSession, article: Article) -> bool:
    """Maqolani Instagramga joylaydi (2 bosqich: konteyner yaratish + e'lon).

    Instagram faqat rasmli postni qabul qiladi; rasmsiz maqola o'tkazib
    yuboriladi."""
    if not article.image_url:
        return False
    if not (IG_ACCESS_TOKEN and IG_USER_ID):
        log.warning("Instagram sozlanmagan (token yoki user ID yo'q)")
        return False

    caption = _build_caption(article)

    # 1-bosqich: media konteyner yaratish
    create = await _post(
        session,
        f"{GRAPH_BASE}/{IG_USER_ID}/media",
        {
            "image_url": article.image_url,
            "caption": caption,
            "access_token": IG_ACCESS_TOKEN,
        },
    )
    creation_id = create.get("id")
    if not creation_id:
        return False

    if not await _wait_ready(session, creation_id):
        return False

    # 2-bosqich: konteynerni e'lon qilish
    published = await _post(
        session,
        f"{GRAPH_BASE}/{IG_USER_ID}/media_publish",
        {"creation_id": creation_id, "access_token": IG_ACCESS_TOKEN},
    )
    return bool(published.get("id"))
