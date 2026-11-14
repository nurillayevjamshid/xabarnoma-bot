import re
import logging
from aiogram import Bot
from aiogram.types import URLInputFile
from aiogram.enums import ParseMode
from html import escape
from config import CHANNEL_ID, FOOTER
from scraper import Article
from translit import to_latin

log = logging.getLogger("xabarnoma")

CAPTION_LIMIT = 1024
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[A-Z«„\"„'O‘O'A-Za-z])")


def _first_paragraph(text: str) -> str:
    """Matnni paragraflarga ajratadi, har birini tozalab \n\n bilan birlashtiradi."""
    if not text:
        return ""
    paragraphs = re.split(r'\n+', text)
    cleaned = []
    for p in paragraphs:
        clean_p = " ".join(p.split())
        if clean_p:
            cleaned.append(clean_p)
    return "\n\n".join(cleaned)


def _build_caption(article: Article) -> str:
    title = escape(to_latin(article.title.strip()))
    summary = escape(to_latin(_first_paragraph(article.body)))
    footer = FOOTER.strip()

    head = f"📌 <b>{title}</b>\n\n"
    tail = f"\n\n{footer}"
    prefix = f"{head}<blockquote>"
    suffix = f"</blockquote>{tail}"
    budget = CAPTION_LIMIT - len(prefix) - len(suffix)

    if budget <= 0:
        return f"{head}{tail}".strip()

    if len(summary) > budget:
        truncated = summary[:budget]
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]
        summary = truncated.rstrip() + "…"

    return f"{prefix}{summary}{suffix}"


async def publish_article(bot: Bot, article: Article) -> bool:
    caption = _build_caption(article)
    try:
        if article.image_url:
            photo = URLInputFile(article.image_url)
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=caption,
                parse_mode=ParseMode.HTML,
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
        log.info("Chop etildi: %s", article.title[:40])
        return True
    except Exception as exc:
        log.error("Chop etishda xato '%s': %s", article.title[:40], exc)
        return False
