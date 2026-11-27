"""Application settings loaded from the process environment and .env."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    secret_key = os.getenv("SECRET_KEY", "insecure-development-key-change-me")
    algorithm = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()
