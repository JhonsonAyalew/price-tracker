# config.py
from dotenv import load_dotenv
import os
import random

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/prices.db")
CSV_PATH = os.getenv("CSV_PATH", "data/products.csv")
PRICE_DROP_THRESHOLD = float(os.getenv("PRICE_DROP_THRESHOLD", 5))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Optional: Scraper settings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

DEFAULT_TIMEOUT = 10  # seconds
PROXY = None  # or "http://yourproxy:port"
