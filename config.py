import os
import json
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TTS_API_KEY = os.getenv("TTS_API_KEY")
ALLOWED_CHAT_IDS = os.getenv("ALLOWED_CHAT_IDS", "[]")
BOT_OWNER_HANDLE = os.getenv("BOT_OWNER_HANDLE", "@novastardev")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing from .env")

if not TTS_API_KEY:
    raise RuntimeError("TTS_API_KEY is missing from .env")

# Parse allowed chat IDs from JSON
try:
    ALLOWED_CHAT_IDS = json.loads(ALLOWED_CHAT_IDS)
except (json.JSONDecodeError, ValueError):
    raise RuntimeError("ALLOWED_CHAT_IDS must be valid JSON array in .env (e.g., [123456789, 987654321])")

if not ALLOWED_CHAT_IDS:
    raise RuntimeError("ALLOWED_CHAT_IDS cannot be empty in .env")