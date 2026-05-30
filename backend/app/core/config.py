import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/elearning.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-dev-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8100")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")


settings = Settings()
