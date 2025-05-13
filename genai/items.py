import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    WEBAPP_URL = os.getenv("WEBAPP_URL")

settings = Settings()