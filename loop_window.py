import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from dedup import init_db, is_posted, mark_posted, cleanup_old
from scraper import fetch_all
from publisher import publish

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("xabarnoma")


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    posted_count = 0

    try:
        # Eski yozuvlarni tozalash
        deleted = cleanup_old(30)
        if deleted:
            log.info(f"Tozalandi: {deleted} ta eski yozuv o'chirildi")

        log.info("Yangiliklar yig'ilmoqda...")
        articles = await fetch_all()
        log.info(f"Topildi: {len(articles)} ta maqola")

        for art in articles:
            if is_posted(art.url, art.title):
                continue
            ok = await publish(bot, art)
            if ok:
                mark_posted(art.url, art.title)
                log.info(f"Yuborildi: {art.title[:60]}")
                posted_count += 1

        log.info(f"Tugadi. Jami yuborildi: {posted_count}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
