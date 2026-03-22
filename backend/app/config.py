import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/agentic_hoops",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://127.0.0.1:5173",
).split(",")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./storage")
API_PORT = int(os.getenv("API_PORT", "8000"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
