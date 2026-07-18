import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Config
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
SESSION_NAME = os.getenv("SESSION_NAME", "xabarnoma_session")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL", "")

# Instagram Config
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
STORAGE_STATE_PATH = "storage_state.json"

# App Config
DOWNLOAD_DIR = "downloads"
LOG_DIR = "logs"

# Ensure directories exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
