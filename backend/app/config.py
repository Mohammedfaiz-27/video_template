"""Application configuration using Pydantic settings."""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    GEMINI_API_KEY: str
    PERPLEXITY_API_KEY: str = ""

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "video_generator"

    # Storage
    UPLOAD_DIR: str = "./storage/uploads"
    PROCESSED_DIR: str = "./storage/processed"
    MAX_FILE_SIZE: int = 524288000  # 500MB in bytes

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def upload_path(self) -> Path:
        """Get absolute path to uploads directory."""
        return Path(self.UPLOAD_DIR).resolve()

    @property
    def processed_path(self) -> Path:
        """Get absolute path to processed directory."""
        return Path(self.PROCESSED_DIR).resolve()

    def ensure_directories(self):
        """Ensure storage directories exist."""
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
