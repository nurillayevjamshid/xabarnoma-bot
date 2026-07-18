import asyncio
import signal
import sys
from telegram_client import TelegramMonitor
from instagram_client import InstagramClient
from utils import logger, clean_downloads
from config_insta import DOWNLOAD_DIR

class XabarnomaBot:
    def __init__(self):
        self.insta = InstagramClient()
        self.tg = TelegramMonitor(self.handle_new_post)
        self.is_running = True

    async def handle_new_post(self, caption: str, media_paths: list[str]):
        logger.info(f"New post received from Telegram. Media count: {len(media_paths)}")
        try:
            if not await self.insta.check_login():
                logger.warning("Instagram session expired. Attempting re-login...")
                if not await self.insta.login():
                    logger.error("Could not re-login to Instagram. Skipping post.")
                    return

            await self.insta.upload_post(caption, media_paths)
        except Exception as e:
            logger.error(f"Failed to process post: {e}")
        finally:
            # Clean up downloaded media after processing
            clean_downloads(DOWNLOAD_DIR)

    async def start(self):
        # Initialize Instagram
        await self.insta.init_browser(headless=True)
        
        # Check login status
        if not await self.insta.check_login():
            logger.error("Instagram not logged in. Please run login.py first.")
            await self.insta.close()
            return

        # Start Telegram monitoring
        try:
            await self.tg.start()
        except Exception as e:
            logger.error(f"Telegram monitor error: {e}")
        finally:
            await self.insta.close()

    def stop(self):
        logger.info("Stopping Xabarnoma Bot...")
        self.is_running = False
        sys.exit(0)

async def main():
    bot = XabarnomaBot()
    
    # Handle Ctrl+C
    loop = asyncio.get_event_loop()
    # In some environments, signal handlers might not work as expected
    # But for a standard Linux environment, this is the correct way
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, bot.stop)
    except NotImplementedError:
        pass

    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
