import re
from aiogram import Bot
from aiogram.types import URLInputFile
from aiogram.enums import ParseMode
from html import escape
from config import CHANNEL_ID, FOOTER
from scraper import Article


CAPTION_LIMIT = 1024
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[A-Z«„\"„'O‘O'A-Za-z])")


def _first_two_sentences(text: str) -> str:
    text = " ".join(text.split())
    parts = SENTENCE_SPLIT.split(text)
    parts = [p.strip() for p in parts if p.strip()]
    return " ".join(parts[:2])


def _build_caption(article: Article) -> str:
    title = escape(article.title.strip())
    summary = _first_two_sentences(article.body)
    summary = escape(summary)
    footer = escape(FOOTER.strip())

    head = f"<b>{title}</b>\n\n"
    tail = f"\n\n{footer}"
    available = CAPTION_LIMIT - len(head) - len(tail) - 5

    if len(summary) > available:
        summary = summary[:available].rsplit(" ", 1)[0] + "..."

    return f"{head}{summary}\n\n{footer}"


async def publish(bot: Bot, article: Article) -> bool:
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
                disable_web_page_preview=True,
            )
        return True
    except Exception as e:
        print(f"[publish] xato: {e}")
        return False
