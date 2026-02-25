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

    # Storage (local fallback — not used when S3 is configured)
    UPLOAD_DIR: str = "./storage/uploads"
    PROCESSED_DIR: str = "./storage/processed"
    MAX_FILE_SIZE: int = 524288000  # 500MB in bytes

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = ""
    S3_UPLOAD_PREFIX: str = "uploads"
    S3_PROCESSED_PREFIX: str = "processed"

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

    @property
    def use_s3(self) -> bool:
        """True if S3 is configured."""
        return bool(self.S3_BUCKET_NAME and self.AWS_ACCESS_KEY_ID)

    def ensure_directories(self):
        """Ensure local temp directory exists (used for processing)."""
        Path("/tmp/video_processing").mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
