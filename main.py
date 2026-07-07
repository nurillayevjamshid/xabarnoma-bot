import asyncio
import random
import time
import logging
from aiogram import Bot
from config import BOT_TOKEN, MIN_INTERVAL_SEC, MAX_INTERVAL_SEC, OWNER_ID
from dedup import init_db, is_posted, mark_posted, cleanup_old
from scraper import fetch_all
from publisher import publish
from sitefeed import append_post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("xabarnoma")

CLEANUP_INTERVAL = 24 * 60 * 60  # 24 soat


async def pick_and_publish(bot: Bot) -> bool:
    """Har chaqiruvda eng eski yuborilmagan postni topadi va FAQAT bittasini
    yuboradi. Shu tariqa postlar birvarakay emas, bitta-bittadan, kelgan
    tartibida (FIFO) tarqatiladi."""
    log.info("Yangiliklar yig'ilmoqda...")
    articles = await fetch_all()
    log.info(f"Topildi: {len(articles)} ta maqola")

    # Eng eski postdan boshlab tekshiramiz (chiqarilgan vaqt bo'yicha xronologik).
    articles.sort(key=lambda a: a.published)
    for art in articles:
        if is_posted(art.url, art.title):
            continue
        ok = await publish(bot, art)
        if ok:
            mark_posted(art.url, art.title)
            append_post(art)
            log.info(f"Yuborildi: {art.title[:60]}")
            return True
    log.info("Yangi yuborilmagan post yo'q")
    return False


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    last_cleanup = time.monotonic()

    try:
        await bot.send_message(OWNER_ID, "Bot ishga tushdi.")
    except Exception as e:
        log.warning(f"Owner ga xabar yuborilmadi: {e}")

    try:
        while True:
            # Kuniga bir marta eski yozuvlarni tozalash
            if time.monotonic() - last_cleanup >= CLEANUP_INTERVAL:
                deleted = cleanup_old(30)
                if deleted:
                    log.info(f"Tozalandi: {deleted} ta eski yozuv o'chirildi")
                last_cleanup = time.monotonic()

            try:
                await pick_and_publish(bot)
            except Exception as e:
                log.exception(f"Tsikl xatosi: {e}")
            delay = random.randint(MIN_INTERVAL_SEC, MAX_INTERVAL_SEC)
            log.info(f"Keyingi yuborishgacha {delay // 60} daqiqa {delay % 60} soniya")
            await asyncio.sleep(delay)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
