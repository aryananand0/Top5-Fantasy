from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # silently ignore unknown env vars
    )

    # --- App ---
    APP_NAME: str = "Top5 Fantasy"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    # Use psycopg v3 driver prefix: postgresql+psycopg://
    DATABASE_URL: str

    # --- Security ---
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str

    # --- CORS ---
    FRONTEND_URL: str = "http://localhost:3000"

    # --- External APIs ---
    FOOTBALL_DATA_API_KEY: str = ""
    THESPORTSDB_API_KEY: str = ""  # optional enrichment only

    # --- Optional infrastructure (not used in MVP) ---
    REDIS_URL: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
