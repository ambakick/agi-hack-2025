"""FastAPI dependencies for dependency injection."""
from app.core.config import settings
from app.services.youtube import YouTubeService
from app.services.gemini import GeminiService
from app.services.elevenlabs import ElevenLabsService


def get_youtube_service() -> YouTubeService:
    """Get YouTube service instance."""
    return YouTubeService(api_key=settings.youtube_api_key)


def get_gemini_service() -> GeminiService:
    """Get Gemini service instance."""
    return GeminiService(api_key=settings.gemini_api_key)


def get_elevenlabs_service() -> ElevenLabsService:
    """Get ElevenLabs service instance."""
    return ElevenLabsService(api_key=settings.elevenlabs_api_key)

