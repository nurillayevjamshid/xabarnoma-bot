import os
import asyncio
from playwright.async_api import async_playwright, Page
from config_insta import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, STORAGE_STATE_PATH
from utils import logger, retry

class InstagramClient:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def init_browser(self, headless=True):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        
        if os.path.exists(STORAGE_STATE_PATH):
            self.context = await self.browser.new_context(storage_state=STORAGE_STATE_PATH)
            logger.info("Loaded Instagram session from storage_state.json")
        else:
            self.context = await self.browser.new_context()
            logger.warning("No session found. Manual login required.")

    async def check_login(self) -> bool:
        page = await self.context.new_page()
        await page.goto("https://www.instagram.com/")
        await asyncio.sleep(3)
        
        if await page.query_selector('svg[aria-label="Home"]'):
            await page.close()
            return True
        
        await page.close()
        return False

    async def login(self):
        page = await self.context.new_page()
        await page.goto("https://www.instagram.com/accounts/login/")
        
        logger.info("Waiting for manual login...")
        # We wait for the user to login manually or provide credentials
        # In this automated flow, we try to fill if credentials exist
        if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
            await page.fill('input[name="username"]', INSTAGRAM_USERNAME)
            await page.fill('input[name="password"]', INSTAGRAM_PASSWORD)
            await page.click('button[type="submit"]')
            await page.wait_for_load_state("networkidle")
        
        # Check if login was successful by looking for the Home icon
        try:
            await page.wait_for_selector('svg[aria-label="Home"]', timeout=60000)
            await self.context.storage_state(path=STORAGE_STATE_PATH)
            logger.info("Login successful and session saved.")
            await page.close()
            return True
        except Exception:
            logger.error("Login failed or timed out.")
            await page.close()
            return False

    @retry(retries=3, delay=10)
    async def upload_post(self, caption: str, media_paths: list[str]):
        if not media_paths:
            logger.warning("No media to upload to Instagram.")
            return

        page = await self.context.new_page()
        try:
            await page.goto("https://www.instagram.com/")
            
            # Click 'Create' button
            try:
                await page.click('svg[aria-label="New post"]', timeout=10000)
            except:
                # Alternative selector for Create button
                await page.click('div[role="button"]:has(svg[aria-label="New post"])', timeout=10000)
            await asyncio.sleep(2)

            # Upload files
            async with page.expect_file_chooser() as fc_info:
                # Instagram web supports multiple files for carousel
                await page.click('button:has-text("Select from computer")')
            file_chooser = await fc_info.value
            await file_chooser.set_files(media_paths)
            
            await asyncio.sleep(3)
            
            # Click 'Next' (Crop)
            await page.wait_for_selector('div[role="button"]:has-text("Next")', timeout=10000)
            await page.click('div[role="button"]:has-text("Next")')
            await asyncio.sleep(2)
            
            # Click 'Next' (Edit/Filters)
            await page.wait_for_selector('div[role="button"]:has-text("Next")', timeout=10000)
            await page.click('div[role="button"]:has-text("Next")')
            await asyncio.sleep(2)

            # Add Caption
            await page.wait_for_selector('div[aria-label="Write a caption..."]', timeout=10000)
            await page.fill('div[aria-label="Write a caption..."]', caption)
            
            # Click 'Share'
            await page.wait_for_selector('div[role="button"]:has-text("Share")', timeout=10000)
            await page.click('div[role="button"]:has-text("Share")')
            
            # Wait for success message
            logger.info("Waiting for sharing confirmation...")
            await page.wait_for_selector('text="Your post has been shared."', timeout=90000)
            logger.info("Post successfully shared on Instagram!")
            
        except Exception as e:
            logger.error(f"Error during Instagram upload: {e}")
            raise e
        finally:
            await page.close()

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
