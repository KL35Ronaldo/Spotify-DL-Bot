# Configuration module for @KL35Bot Spotify Telegram Bot.
# Handles environment variables and application constants.

import os, sys, logging
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)
load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "./temp_downloads"))
    MAX_FILE_SIZE_MB: int = 50
    DOWNLOAD_TIMEOUT: int = 120
    API_TIMEOUT: int = 30
    AUDIO_BITRATE: str = "320"
    AUDIO_FORMAT: str = "mp3"
    BOT_NAME: str = "@KL35Bot"
    BOT_VERSION: str = "1.0.0"
    TEMP_STORAGE: int = -1001602310133

    @classmethod
    def validate(cls) -> bool:
        missing = []

        if not cls.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        if not cls.SPOTIFY_CLIENT_ID:
            missing.append("SPOTIFY_CLIENT_ID")
        if not cls.SPOTIFY_CLIENT_SECRET:
            missing.append("SPOTIFY_CLIENT_SECRET")

        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            return False

        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)

        return True

if not Config.validate():
    logger.critical("Configuration validation failed. Exiting.")
    sys.exit(1)
