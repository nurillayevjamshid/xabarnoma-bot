import asyncio
import functools
import os
import shutil
from loguru import logger
from config_insta import LOG_DIR

# Setup logging
logger.add(os.path.join(LOG_DIR, "app.log"), rotation="10 MB", level="INFO")

def retry(retries=3, delay=5):
    """Decorator for retrying functions on failure."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {i+1} failed for {func.__name__}: {e}")
                    await asyncio.sleep(delay)
            logger.error(f"All {retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

def clean_downloads(directory: str):
    """Deletes all files in the specified directory."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f"Failed to delete {file_path}. Reason: {e}")
