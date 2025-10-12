"""Application configuration."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # App
    app_env: str = "local"
    base_url: str = "http://localhost:8000"

    # Security
    secret_key: str
    jwt_alg: str = "HS256"
    access_token_expire_min: int = 30
    refresh_token_expire_min: int = 43200

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # OCR
    ocr_enabled: bool = True
    tesseract_cmd: str = "/usr/bin/tesseract"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

