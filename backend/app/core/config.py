"""Application configuration using Pydantic settings."""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    youtube_api_key: str
    gemini_api_key: str
    elevenlabs_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        # Load `.env` from the backend directory regardless of the current working directory.
        # (This avoids startup failures when running uvicorn from the repo root.)
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        case_sensitive = False


settings = Settings()

