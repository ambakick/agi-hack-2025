"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import discovery, transcripts, analysis, outline, script, tts

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

