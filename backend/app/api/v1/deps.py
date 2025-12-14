"""FastAPI dependencies for dependency injection."""
from app.core.config import settings
from app.services.youtube import YouTubeService
from app.services.gemini import GeminiService
from app.services.google_tts import GoogleTTSService


def get_youtube_service() -> YouTubeService:
    """Get YouTube service instance."""
    return YouTubeService(api_key=settings.youtube_api_key)


def get_gemini_service() -> GeminiService:
    """Get Gemini service instance."""
    return GeminiService(api_key=settings.gemini_api_key)


def get_google_tts_service() -> GoogleTTSService:
    """Get Google TTS service instance."""
    return GoogleTTSService(api_key=settings.google_tts_api_key)

