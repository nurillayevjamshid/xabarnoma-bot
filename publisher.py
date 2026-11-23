import re
import asyncio
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


def _format_body(text: str) -> str:
    """Matn paragraflarini saqlab tozalaydi."""
    if not text:
        return ""
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n+', text) if p.strip()]
    cleaned = []
    for p in paragraphs:
        lines = [ln.strip() for ln in p.splitlines() if ln.strip()]
        if any(l.startswith(("▪️", "•", "-", "—")) for l in lines):
            cleaned.append("\n".join(lines))
        else:
            cleaned.append(" ".join(lines))
    return "\n\n".join(cleaned)


def _build_caption(article: Article) -> str:
    title = escape(to_latin(article.title.strip()))
    summary = escape(to_latin(_format_body(article.body)))
    footer = FOOTER.strip()

    head = f"📌 <b>{title}</b>\n\n"
    tail = f"\n\n{footer}"
    prefix = f"{head}<blockquote>"
    suffix = f"</blockquote>{tail}"

    max_body_len = CAPTION_LIMIT - len(prefix) - len(suffix)

    if len(summary) > max_body_len:
        summary = summary[:max_body_len - 3].rsplit(" ", 1)[0]
        if "&" in summary and ";" not in summary.rsplit("&", 1)[1]:
            summary = summary.rsplit("&", 1)[0]
        summary += "..."

    return f"{prefix}{summary}{suffix}"


async def _send_text(bot: Bot, caption: str) -> None:
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=caption,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def publish(bot: Bot, article: Article) -> bool:
    caption = _build_caption(article)

    # Video bo'lsa, post faqat video sifatida yuboriladi.
    if article.video_url:
        try:
            video = URLInputFile(article.video_url, filename="news_video.mp4")
            await bot.send_video(
                chat_id=CHANNEL_ID,
                video=video,
                caption=caption,
                parse_mode=ParseMode.HTML,
                supports_streaming=True,
            )
            return True
        except Exception as error:
            log.warning(f"Video yuborishda xatolik/timeout: {error}")
            # Telegram ba'zida 500 yoki HTTP timeout qaytarsa ham, videoni fonda yuklab kanalga chiqarib qo'yadi.
            await asyncio.sleep(5)
            try:
                from dedup import is_in_telegram_channel
                if is_in_telegram_channel(article.title, force_refresh=True):
                    log.info(f"Video kanalga yetib borgani tasdiqlandi: {article.title[:60]}")
                    return True
            except Exception as e:
                log.warning(f"Live channel tekshirishda xatolik: {e}")
            return False

    # Rasm bo'lsa, rasm bilan yuborishga urinamiz.
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
            log.warning(f"Photo send failed, trying text only: {e}")

    try:
        await _send_text(bot, caption)
        return True
    except Exception as e:
        log.error(f"Yuborib bo'lmadi: {e}")
        # Matn yuborishda ham timeout bo'lsa, kanalni tekshirib ko'ramiz
        try:
            from dedup import is_in_telegram_channel
            if is_in_telegram_channel(article.title, force_refresh=True):
                log.info(f"Matnli post kanalga yetib borgani tasdiqlandi: {article.title[:60]}")
                return True
        except Exception:
            pass
        return False


publish_article = publish
