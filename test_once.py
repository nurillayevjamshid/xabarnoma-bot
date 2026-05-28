import asyncio
from aiogram import Bot
from config import BOT_TOKEN
from dedup import init_db
from main import pick_and_publish


async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    try:
        await pick_and_publish(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
