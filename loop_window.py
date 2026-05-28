import asyncio
import random
import time
import logging
from aiogram import Bot
from config import BOT_TOKEN, MIN_INTERVAL_SEC, MAX_INTERVAL_SEC
from dedup import init_db
from main import pick_and_publish


WINDOW_SECONDS = 55 * 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("xabarnoma")


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    start = time.monotonic()
    posted_count = 0
    try:
        while True:
            elapsed = time.monotonic() - start
            if elapsed >= WINDOW_SECONDS:
                log.info(f"Vaqt oynasi tugadi. Yuborilgan: {posted_count}")
                break
            try:
                ok = await pick_and_publish(bot)
                if ok:
                    posted_count += 1
            except Exception as e:
                log.exception(f"Tsikl xatosi: {e}")

            delay = random.randint(MIN_INTERVAL_SEC, MAX_INTERVAL_SEC)
            remaining = WINDOW_SECONDS - (time.monotonic() - start)
            if remaining <= 30:
                log.info("Vaqt oynasi tugamoqda, chiqilmoqda")
                break
            delay = min(delay, int(remaining) - 5)
            log.info(f"Keyingi yuborishgacha {delay // 60} daq {delay % 60} son")
            await asyncio.sleep(delay)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
