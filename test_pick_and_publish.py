import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN
from dedup import init_db
from main import pick_and_publish

logging.basicConfig(level=logging.INFO)

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    print("Running pick_and_publish...")
    success = await pick_and_publish(bot)
    print(f"Result: {success}")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
