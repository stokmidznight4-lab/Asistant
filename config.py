import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OWNER_ID = os.getenv("OWNER_ID", "")

API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY", ""),
    "gemini": os.getenv("GEMINI_API_KEY", ""),
    "grok": os.getenv("XAI_API_KEY", ""),
    "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
    "kimi": os.getenv("MOONSHOT_API_KEY", ""),
}

MODEL_NAMES = {
    "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "gemini": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    "grok": os.getenv("XAI_MODEL", "grok-4.3"),
    "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
    "kimi": os.getenv("MOONSHOT_MODEL", "kimi-k2.6"),
}

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini")

# Nama tampilan yang ramah untuk tiap provider
MODEL_LABELS = {
    "openai": "🟢 OpenAI (GPT)",
    "gemini": "🔵 Google Gemini",
    "grok": "⚫ Grok (xAI)",
    "deepseek": "🐳 DeepSeek",
    "kimi": "🌙 Kimi (Moonshot)",
}

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
