import asyncio
import os
import random
import time
import logging
import subprocess
from aiogram import Bot
from config import BOT_TOKEN, MIN_INTERVAL_SEC, MAX_INTERVAL_SEC, DB_PATH
from dedup import init_db, cleanup_old
from main import pick_and_publish

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("xabarnoma")

# Bitta GitHub Actions ishi qancha vaqt aylanadi (6 soatlik limitdan past).
RUN_SECONDS = int(os.getenv("RUN_SECONDS", 20400))      # ~5 soat 40 daqiqa
# posted.db ni git'ga necha soniyada bir saqlash (dublikatni oldini olish uchun).
COMMIT_INTERVAL = int(os.getenv("COMMIT_INTERVAL", 1800))  # 30 daqiqa
# posted.db ni git'ga commit/push qilish kerakmi (Actions ichida = 1).
COMMIT_DB = os.getenv("COMMIT_DB", "0") == "1"


def _commit_db():
    """posted.db o'zgargan bo'lsa, git'ga saqlaydi. Keyingi run shu bazani
    o'qib, allaqachon yuborilgan postlarni qayta yubormaydi."""
    try:
        subprocess.run(["git", "add", DB_PATH], check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
            return  # o'zgarish yo'q
        subprocess.run(
            ["git", "commit", "-m", "chore: update posted.db [skip ci]"], check=True
        )
        subprocess.run(["git", "pull", "--rebase", "--autostash"], check=False)
        subprocess.run(["git", "push"], check=False)
        log.info("posted.db saqlandi")
    except Exception as e:
        log.warning(f"posted.db saqlanmadi: {e}")


async def main():
    init_db()
    cleanup_old(30)
    bot = Bot(token=BOT_TOKEN)
    deadline = time.monotonic() + RUN_SECONDS
    last_commit = time.monotonic()

    log.info(f"Loop boshlandi, ~{RUN_SECONDS // 60} daqiqa ishlaydi")
    try:
        while time.monotonic() < deadline:
            try:
                await pick_and_publish(bot)
            except Exception as e:
                log.exception(f"Tsikl xatosi: {e}")

            # Davriy ravishda posted.db ni saqlaymiz (crash bo'lsa ham yo'qolmasin)
            if COMMIT_DB and time.monotonic() - last_commit >= COMMIT_INTERVAL:
                _commit_db()
                last_commit = time.monotonic()

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            delay = random.randint(MIN_INTERVAL_SEC, MAX_INTERVAL_SEC)
            log.info(f"Keyingi yuborishgacha {delay // 60} daqiqa {delay % 60} soniya")
            await asyncio.sleep(min(delay, remaining))
    finally:
        await bot.session.close()
        if COMMIT_DB:
            _commit_db()  # ish tugashidan oldin oxirgi marta saqlash
        log.info("Loop tugadi")


if __name__ == "__main__":
    asyncio.run(main())
