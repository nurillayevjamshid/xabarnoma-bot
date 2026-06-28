import asyncio
import random
import time
import logging
import aiohttp
from aiogram import Bot
from config import (
    BOT_TOKEN,
    MIN_INTERVAL_SEC,
    MAX_INTERVAL_SEC,
    OWNER_ID,
    IG_ENABLED,
    IG_ACCESS_TOKEN,
    IG_USER_ID,
    IG_MIN_INTERVAL_SEC,
    IG_MAX_INTERVAL_SEC,
    IG_DAILY_LIMIT,
)
from dedup import init_db, is_posted, mark_posted, count_recent, cleanup_old
from scraper import fetch_all
from publisher import publish
import instagram

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
            log.info(f"Telegramga yuborildi: {art.title[:60]}")
            return True
    log.info("Yangi yuborilmagan post yo'q")
    return False


async def pick_and_publish_ig(session: aiohttp.ClientSession) -> bool:
    """Instagram uchun: rasmli, hali Instagramga yuborilmagan eng eski postni
    topadi va bittasini joylaydi. Kunlik limitga rioya qiladi."""
    sent_24h = count_recent(24, table="posted_ig")
    if sent_24h >= IG_DAILY_LIMIT:
        log.info(f"Instagram kunlik limitga yetildi ({sent_24h}/{IG_DAILY_LIMIT})")
        return False

    articles = await fetch_all()
    articles.sort(key=lambda a: a.published)
    for art in articles:
        if not art.image_url:
            continue  # Instagram rasmsiz postni qabul qilmaydi
        if is_posted(art.url, art.title, table="posted_ig"):
            continue
        ok = await instagram.publish(session, art)
        if ok:
            mark_posted(art.url, art.title, table="posted_ig")
            log.info(f"Instagramga yuborildi: {art.title[:60]}")
            return True
    log.info("Instagram uchun yangi (rasmli) post yo'q")
    return False


async def telegram_loop(bot: Bot):
    last_cleanup = time.monotonic()
    while True:
        # Kuniga bir marta eski yozuvlarni tozalash
        if time.monotonic() - last_cleanup >= CLEANUP_INTERVAL:
            deleted = cleanup_old(30, table="posted") + cleanup_old(30, table="posted_ig")
            if deleted:
                log.info(f"Tozalandi: {deleted} ta eski yozuv o'chirildi")
            last_cleanup = time.monotonic()

        try:
            await pick_and_publish(bot)
        except Exception as e:
            log.exception(f"Telegram tsikl xatosi: {e}")
        delay = random.randint(MIN_INTERVAL_SEC, MAX_INTERVAL_SEC)
        log.info(f"Telegram: keyingi yuborishgacha {delay // 60} daqiqa {delay % 60} soniya")
        await asyncio.sleep(delay)


async def instagram_loop():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await pick_and_publish_ig(session)
            except Exception as e:
                log.exception(f"Instagram tsikl xatosi: {e}")
            delay = random.randint(IG_MIN_INTERVAL_SEC, IG_MAX_INTERVAL_SEC)
            log.info(f"Instagram: keyingi yuborishgacha {delay // 60} daqiqa {delay % 60} soniya")
            await asyncio.sleep(delay)


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)

    try:
        await bot.send_message(OWNER_ID, "Bot ishga tushdi.")
    except Exception as e:
        log.warning(f"Owner ga xabar yuborilmadi: {e}")

    tasks = [telegram_loop(bot)]
    if IG_ENABLED and IG_ACCESS_TOKEN and IG_USER_ID:
        log.info("Instagram avto-post yoqilgan")
        tasks.append(instagram_loop())
    elif IG_ENABLED:
        log.warning("IG_ENABLED yoqilgan, lekin IG_ACCESS_TOKEN/IG_USER_ID yo'q — Instagram o'chirildi")

    try:
        await asyncio.gather(*tasks)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
