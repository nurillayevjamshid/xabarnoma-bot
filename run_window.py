import asyncio
import os
import re
import random
import time
import logging
import subprocess
from collections import defaultdict
from aiogram import Bot
from config import BOT_TOKEN, MIN_INTERVAL_SEC, MAX_INTERVAL_SEC, DB_PATH
from dedup import init_db, cleanup_old, is_posted, mark_posted
from scraper import fetch_all
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
# SEED=1 bo'lsa: hozir kanallarda turgan postlar "yuborilgan" deb belgilanadi,
# har kanaldan faqat ENG OXIRGISI qoldiriladi. Shunda eski postlar yuborilmaydi,
# faqat eng so'nggi post va bundan keyingi yangilari yuboriladi. Bir martalik.
SEED = os.getenv("SEED", "0") == "1"


def _post_id(url: str) -> int:
    m = re.search(r"/(\d+)$", url.rstrip("/"))
    return int(m.group(1)) if m else 0


def _channel(url: str) -> str:
    parts = url.rstrip("/").split("/")
    return parts[-2] if len(parts) >= 2 else "?"


async def seed_baseline():
    """Boshlang'ich nuqtani belgilaydi: hozir ko'rinib turgan barcha postlarni
    'yuborilgan' deb belgilaydi, har kanaldan eng oxirgisidan tashqari."""
    log.info("SEED: boshlang'ich nuqta belgilanmoqda...")
    articles = await fetch_all()
    by_ch = defaultdict(list)
    for a in articles:
        by_ch[_channel(a.url)].append(a)

    marked = 0
    for ch, arts in by_ch.items():
        arts.sort(key=lambda a: _post_id(a.url))  # eng oxirgisi (katta id) oxirda
        for a in arts[:-1]:  # eng oxirgisini qoldiramiz (u yuboriladi)
            if not is_posted(a.url, a.title):
                mark_posted(a.url, a.title)
                marked += 1
        if arts:
            log.info(f"SEED: {ch} — eng oxirgisi qoldirildi: {arts[-1].url}")
    log.info(f"SEED: {marked} ta eski post belgilandi (yuborilmaydi)")


def _commit_db():
    """posted.db o'zgargan bo'lsa, git'ga saqlaydi. Keyingi run shu bazani
    o'qib, allaqachon yuborilgan postlarni qayta yubormaydi."""
    try:
        subprocess.run(["git", "add", DB_PATH, "docs"], check=True)
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

    if SEED:
        await seed_baseline()
        if COMMIT_DB:
            _commit_db()

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
