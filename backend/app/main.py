"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import settings
from app.api.v1 import discovery, transcripts, analysis, outline, script, tts, video, upload
from app.api.v1.endpoints import cache as cache_endpoints

# Create FastAPI app
app = FastAPI(
    title="AI Podcast Generator API",
    description="Generate complete podcast episodes from topics using AI",
    version="1.0.0",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(discovery.router, prefix="/api/v1", tags=["discovery"])
app.include_router(transcripts.router, prefix="/api/v1", tags=["transcripts"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(outline.router, prefix="/api/v1", tags=["outline"])
app.include_router(script.router, prefix="/api/v1", tags=["script"])
app.include_router(tts.router, prefix="/api/v1", tags=["tts"])
app.include_router(video.router, prefix="/api/v1", tags=["video"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(cache_endpoints.router, prefix="/api/v1/cache", tags=["cache"])

# Mount static file directories for video and audio output
video_output_path = Path(settings.video_output_dir).resolve()
audio_output_path = Path(settings.audio_output_dir).resolve()
uploads_path = Path("uploads").resolve()

# Create directories if they don't exist
video_output_path.mkdir(parents=True, exist_ok=True)
audio_output_path.mkdir(parents=True, exist_ok=True)
uploads_path.mkdir(parents=True, exist_ok=True)

# Mount static file serving
app.mount("/video_output", StaticFiles(directory=str(video_output_path)), name="video_output")
app.mount("/audio_output", StaticFiles(directory=str(audio_output_path)), name="audio_output")
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Podcast Generator API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

