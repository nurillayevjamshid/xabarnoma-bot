import asyncio
from scraper import fetch_all

async def main():
    print("Fetching articles...")
    articles = await fetch_all()
    print(f"Found {len(articles)} articles.")
    for i, art in enumerate(articles):
        print(f"\n--- Article {i+1} ---")
        print(f"URL: {art.url}")
        print(f"Title: {art.title}")
        print(f"Body: {art.body[:200]}...")
        print(f"Image: {art.image_url}")
        print(f"Video: {art.video_url}")

if __name__ == "__main__":
    asyncio.run(main())
