import asyncio
import re
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin
from config import USER_AGENT
from translit import to_latin, is_cyrillic


@dataclass
class Article:
    url: str
    title: str
    body: str
    image_url: Optional[str]


HEADERS = {"User-Agent": USER_AGENT}
MAX_PER_SOURCE = 15


async def _fetch(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url, headers=HEADERS, timeout=20) as resp:
            if resp.status != 200:
                return None
            return await resp.text()
    except Exception:
        return None


def _extract_body_and_image(html: str, body_selectors: list[str]) -> tuple[str, Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    body_el = None
    for sel in body_selectors:
        body_el = soup.select_one(sel)
        if body_el:
            break
    if not body_el:
        body_el = soup.select_one("article") or soup.body
    if body_el:
        for tag in body_el.select("script, style, iframe, .related, .ads, .advert, .share, .tags, nav, footer, .cookie, .cookies"):
            tag.decompose()
        paragraphs = [p.get_text(" ", strip=True) for p in body_el.find_all("p")]
        bad_markers = ("cookie", "cookies-fayl", "maxfiylik siyosati", "rozilik bildirasiz")
        meta_re = re.compile(r"^\d+\s+(yan|fev|mar|apr|may|iyun|iyul|avg|sen|okt|noy|dek)", re.I)
        cleaned = []
        for p in paragraphs:
            if len(p) <= 20:
                continue
            low = p.lower()
            if any(m in low for m in bad_markers):
                continue
            if "visibility" in low and "timer" in low:
                continue
            if meta_re.match(p) and ("visibility" in low or "timer" in low or "daqiqa" in low):
                continue
            cleaned.append(p)
        body = "\n\n".join(cleaned)
    else:
        body = ""

    og = soup.select_one('meta[property="og:image"]') or soup.select_one('meta[name="og:image"]')
    img = og.get("content") if og else None
    return body, img


def _extract_title(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "lxml")
    og = soup.select_one('meta[property="og:title"]')
    if og and og.get("content"):
        return og["content"].strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    if soup.title:
        return soup.title.get_text(strip=True)
    return None


async def _scrape_listing(
    session, list_url: str, link_pattern: re.Pattern, body_selectors: list[str]
) -> list[Article]:
    list_html = await _fetch(session, list_url)
    if not list_html:
        return []
    soup = BeautifulSoup(list_html, "lxml")
    seen = set()
    urls = []
    for a in soup.find_all("a", href=True):
        href = urljoin(list_url, a["href"])
        if link_pattern.search(href) and href not in seen:
            seen.add(href)
            urls.append(href)
        if len(urls) >= MAX_PER_SOURCE:
            break

    async def _one(u):
        h = await _fetch(session, u)
        if not h:
            return None
        title = _extract_title(h)
        if not title:
            return None
        body, img = _extract_body_and_image(h, body_selectors)
        if not body:
            return None
        return Article(url=u, title=title, body=body, image_url=img)

    results = await asyncio.gather(*(_one(u) for u in urls), return_exceptions=True)
    return [r for r in results if isinstance(r, Article)]


async def _kun_uz(session) -> list[Article]:
    return await _scrape_listing(
        session,
        "https://kun.uz/uz/news/list",
        re.compile(r"kun\.uz/(?:uz/)?news/\d{4}/\d{2}/\d{2}/"),
        ["div.single-content", "div.article-content", "div.post-content"],
    )


async def _qalampir_uz(session) -> list[Article]:
    return await _scrape_listing(
        session,
        "https://qalampir.uz/uz",
        re.compile(r"/uz/news/[a-z0-9\-]+-\d+"),
        ["div.news-text", "div.article__content", "div.single-text", "div.post-content"],
    )


async def _aniq_uz(session) -> list[Article]:
    rss = await _fetch(session, "https://aniq.uz/uz/yangiliklar/rss")
    if not rss:
        return []
    feed = feedparser.parse(rss)
    body_selectors = ["div.news-item-detail div.news-item_text", "div.news-item_text"]

    async def _one(entry):
        url = entry.link
        if "://aniq.uz/y/" in url:
            url = url.replace("://aniq.uz/y/", "://aniq.uz/uz/y/")
        h = await _fetch(session, url)
        if not h:
            return None
        title = _extract_title(h) or entry.title
        body, img = _extract_body_and_image(h, body_selectors)
        if not body:
            return None
        return Article(url=url, title=title, body=body, image_url=img)

    results = await asyncio.gather(
        *(_one(e) for e in feed.entries[:MAX_PER_SOURCE]),
        return_exceptions=True,
    )
    return [r for r in results if isinstance(r, Article)]


_TG_CHANNELS = ["Geointriga_uz"]


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
        lines = [ln.strip() for ln in raw.splitlines()]
        lines = [ln for ln in lines if ln and not handle_re.fullmatch(ln) and "t.me/" not in ln.lower()]
        if not lines:
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
        tasks = [
            _kun_uz(session),
            _qalampir_uz(session),
            _aniq_uz(session),
        ]
        for ch in _TG_CHANNELS:
            tasks.append(_telegram_channel(session, ch))
        results = await asyncio.gather(*tasks, return_exceptions=True)
    articles: list[Article] = []
    for r in results:
        if isinstance(r, list):
            articles.extend(r)
    return articles
