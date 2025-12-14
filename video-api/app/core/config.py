"""Application configuration using Pydantic settings."""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        case_sensitive=False,
    )
    
    # API Keys
    gemini_api_key: str
    google_tts_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000"
    
    # Output Directories
    video_output_dir: str = "./video_output"
    audio_output_dir: str = "./audio_output"
    
    # Video Generation Settings
    max_scene_duration: int = 8  # seconds (Veo max)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()

