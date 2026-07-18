import asyncio
from instagram_client import InstagramClient
from utils import logger

async def main():
    insta = InstagramClient()
    await insta.init_browser(headless=False) # Open browser for manual login if needed
    
    logged_in = await insta.check_login()
    if not logged_in:
        logger.info("Starting login process...")
        success = await insta.login()
        if success:
            logger.info("Session created successfully!")
        else:
            logger.error("Failed to create session.")
    else:
        logger.info("Already logged in. Session is valid.")
    
    await insta.close()

if __name__ == "__main__":
    asyncio.run(main())
