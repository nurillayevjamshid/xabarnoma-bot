import re
import logging
from aiogram import Bot
from aiogram.types import URLInputFile
from aiogram.enums import ParseMode
from html import escape
from config import CHANNEL_ID, FOOTER
from scraper import Article


log = logging.getLogger("xabarnoma")

CAPTION_LIMIT = 1024
SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[A-Z«„\"„'O‘O'A-Za-z])")


def _first_paragraph(text: str) -> str:
    """Matndan birinchi to'liq paragrafni oladi."""
    text = " ".join(text.split())
    parts = text.split("\n\n")
    for p in parts:
        p = p.strip()
        if len(p) > 30:
            return p
    # Agar paragraf topilmasa, birinchi 500 belgini qaytar
    return text[:500].rsplit(" ", 1)[0] + "..." if len(text) > 500 else text


def _build_caption(article: Article) -> str:
    title = escape(article.title.strip())
    summary = _first_paragraph(article.body)
    summary = escape(summary)
    footer = escape(FOOTER.strip())

    head = f"<b>{title}</b>\n\n"
    tail = f"\n\n{footer}"
    available = CAPTION_LIMIT - len(head) - len(tail) - 5

    if len(summary) > available:
        summary = summary[:available].rsplit(" ", 1)[0] + "..."

    return f"{head}{summary}\n\n{footer}"


async def _send_text(bot: Bot, caption: str) -> None:
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=caption,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def publish(bot: Bot, article: Article) -> bool:
    caption = _build_caption(article)

    # Rasm bo'lsa, avval rasm bilan yuborishga urinamiz.
    if article.image_url:
        try:
            photo = URLInputFile(article.image_url)
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=caption,
                parse_mode=ParseMode.HTML,
            )
            return True
        except Exception as e:
            # Rasmni Telegram yuklay olmasa, post yo'qolib ketmasligi uchun
            # matn ko'rinishida yuboramiz.
            log.warning(f"Rasm bilan yuborilmadi, matn sifatida urinilmoqda: {e}")

    try:
        await _send_text(bot, caption)
        return True
    except Exception as e:
        log.error(f"Yuborib bo'lmadi: {e}")
        return False
