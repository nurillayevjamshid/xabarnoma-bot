import asyncio
import logging
from aiogram import Bot
from config import BOT_TOKEN, OWNER_ID
from scraper import Article
from publisher import publish

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    test_article = Article(
        url="https://t.me/test/1",
        title="Test Title from Manus",
        body="Test Body from Manus. This is a test post to verify the publisher works.",
        image_url="https://picsum.photos/200/300",
        published="2026-08-06T19:00:00"
    )
    
    print("Attempting to publish test article...")
    success = await publish(bot, test_article)
    print(f"Publish result: {success}")
    
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
