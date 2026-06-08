import asyncio
import re
import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
from config import USER_AGENT, TELEGRAM_CHANNELS
from translit import to_latin, is_cyrillic


@dataclass
class Article:
    url: str
    title: str
    body: str
    image_url: Optional[str]


HEADERS = {"User-Agent": USER_AGENT}


async def _fetch(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url, headers=HEADERS, timeout=20) as resp:
            if resp.status != 200:
                return None
            return await resp.text()
    except Exception:
        return None


async def _telegram_channel(session, username: str) -> list[Article]:
    url = f"https://t.me/s/{username}"
    html = await _fetch(session, url)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    posts = soup.select("div.tgme_widget_message_wrap")
    out: list[Article] = []
    handle_re = re.compile(r"@\w+", re.I)
    for post in posts:
        msg = post.select_one("div.tgme_widget_message")
        if not msg:
            continue
        post_id = msg.get("data-post")
        if not post_id:
            continue
        text_el = post.select_one("div.tgme_widget_message_text")
        if not text_el:
            continue
        for br in text_el.find_all("br"):
            br.replace_with("\n")
        raw = text_el.get_text("\n", strip=True)
        # Barcha URL va havolalarni tozalash
        url_re = re.compile(r'https?://\S+', re.I)
        lines = [ln.strip() for ln in raw.splitlines()]
        lines = [url_re.sub('', ln).strip() for ln in lines]
        lines = [ln for ln in lines if ln and not handle_re.fullmatch(ln) and "t.me/" not in ln.lower() and "instagram.com" not in ln.lower()]
        lines = [ln for ln in lines if ln]
        if not lines:
            continue

        # Reklama postlarini filtrlash
        if re.search(r"#реклама|#reklama", raw, re.I):
            continue

        def _has_letters(s: str) -> bool:
            return any(c.isalpha() for c in s)

        title_idx = next((i for i, ln in enumerate(lines) if _has_letters(ln) and len(ln) > 5), 0)
        title = lines[title_idx]
        body_parts = lines[title_idx + 1:]
        body = "\n\n".join(body_parts) if body_parts else title

        if is_cyrillic(title):
            title = to_latin(title)
        if is_cyrillic(body):
            body = to_latin(body)

        img = None
        photo_wrap = post.select_one("a.tgme_widget_message_photo_wrap")
        if photo_wrap and photo_wrap.get("style"):
            m = re.search(r"url\(['\"]?([^'\")]+)['\"]?\)", photo_wrap["style"])
            if m:
                img = m.group(1)

        post_url = f"https://t.me/{post_id}"
        out.append(Article(url=post_url, title=title, body=body, image_url=img))
    return out


async def fetch_all() -> list[Article]:
    connector = aiohttp.TCPConnector(limit=10, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_telegram_channel(session, ch) for ch in TELEGRAM_CHANNELS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    articles: list[Article] = []
    for r in results:
        if isinstance(r, list):
            articles.extend(r)
    return articles
