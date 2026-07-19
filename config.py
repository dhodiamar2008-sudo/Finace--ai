import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/finance.db")

if not GEMINI_API_KEY:
    print("[WARN] GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
