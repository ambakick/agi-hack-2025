"""Video generation API endpoints."""

import logging
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.core.config import settings
from app.models.schemas import (
    TranscriptInput,
    SnippetExtractionResponse,
    SceneGenerationResponse,
    VideoGenerationResponse,
    AudioGenerationResponse,
    VideoStitchRequest,
    VideoStitchResponse,
    AudioSyncRequest,
    AudioSyncResponse,
    VideoGenerationRequest,
    VideoGenerationFullResponse,
    Snippet,
    SceneDescription,
)
from app.services.snippet_extractor import SnippetExtractor
from app.services.scene_generator import SceneGenerator
from app.services.veo_service import VeoService
from app.services.video_audio_service import VideoAudioService
from app.services.video_stitcher import VideoStitcher
from app.services.audio_sync import AudioSync

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
snippet_extractor = SnippetExtractor(settings.gemini_api_key)
scene_generator = SceneGenerator(settings.gemini_api_key)
veo_service = VeoService(settings.gemini_api_key)
audio_service = VideoAudioService(settings.google_tts_api_key)
video_stitcher = VideoStitcher()
audio_sync = AudioSync()

def _normalize_voice_id(voice_id: Optional[str]) -> Optional[str]:
    """
    Normalize user-provided voice_id values.

    Frontends sometimes send the literal string "default" to mean "use whatever
    the backend's default voice is". ElevenLabs expects a real voice_id, so we
    map sentinel/blank values to None to trigger our service defaults.
    """
    if voice_id is None:
        return None
    normalized = voice_id.strip()
    if normalized == "" or normalized.lower() == "default":
        return None
    return normalized


@router.post("/extract-snippets", response_model=SnippetExtractionResponse)
async def extract_snippets(
    transcript_input: TranscriptInput,
    max_snippets: int = 5
):
    """
    Extract interesting snippets from transcript.
    
    Args:
        transcript_input: Transcript in plain text or JSON format
        max_snippets: Maximum number of snippets to extract
        
    Returns:
        SnippetExtractionResponse with extracted snippets
    """
    try:
        result = await snippet_extractor.extract_snippets(
            transcript_input,
            max_snippets=max_snippets
        )
        return result
    except Exception as e:
        logger.error(f"Error extracting snippets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-scenes", response_model=SceneGenerationResponse)
async def generate_scenes(snippets: List[Snippet]):
    """
    Generate 8-second scene descriptions from snippets.
    
    Args:
        snippets: List of extracted snippets
        
    Returns:
        SceneGenerationResponse with scene descriptions
    """
    try:
        result = await scene_generator.generate_scenes(snippets)
        return result
    except Exception as e:
        logger.error(f"Error generating scenes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-videos", response_model=VideoGenerationResponse)
async def generate_videos(scenes: List[SceneDescription]):
    """
    Generate video clips using Veo 3.1.
    
    Args:
        scenes: List of scene descriptions
        
    Returns:
        VideoGenerationResponse with generated video clips
    """
    try:
        result = await veo_service.generate_videos(scenes)
        return result
    except Exception as e:
        logger.error(f"Error generating videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-audio", response_model=AudioGenerationResponse)
async def generate_audio(
    scenes: List[SceneDescription],
    voice_id: Optional[str] = None
):
    """
    Generate audio clips using ElevenLabs.
    
    Args:
        scenes: List of scene descriptions
        voice_id: Optional ElevenLabs voice ID
        
    Returns:
        AudioGenerationResponse with generated audio clips
    """
    try:
        normalized_voice_id = _normalize_voice_id(voice_id)
        result = await audio_service.generate_audio_clips(scenes, voice_id=normalized_voice_id)
        return result
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stitch-videos", response_model=VideoStitchResponse)
async def stitch_videos(request: VideoStitchRequest):
    """
    Stitch multiple video clips into a single video.
    
    Args:
        request: VideoStitchRequest with video paths
        
    Returns:
        VideoStitchResponse with stitched video path
    """
    try:
        result = await video_stitcher.stitch_videos(
            request.video_paths,
            request.output_path
        )
        return result
    except Exception as e:
        logger.error(f"Error stitching videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-audio", response_model=AudioSyncResponse)
async def add_audio(request: AudioSyncRequest):
    """
    Add audio to video, ensuring perfect synchronization.
    
    Args:
        request: AudioSyncRequest with video and audio paths
        
    Returns:
        AudioSyncResponse with final video path
    """
    try:
        result = await audio_sync.sync_audio(
            request.video_path,
            request.audio_path,
            request.output_path
        )
        return result
    except Exception as e:
        logger.error(f"Error adding audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-video", response_model=VideoGenerationFullResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    Video-only pipeline: Extract snippets, generate scenes, generate videos, and stitch.
    (No ElevenLabs audio generation / no audio sync.)
    
    Args:
        request: VideoGenerationRequest with transcript
        
    Returns:
        VideoGenerationFullResponse with complete pipeline results
    """
    try:
        logger.info("Starting video-only generation pipeline...")
        
        # Step 1: Extract snippets
        transcript_input = TranscriptInput(
            transcript=request.transcript,
            format=request.transcript_format
        )
        snippets_response = await snippet_extractor.extract_snippets(
            transcript_input,
            # Default to 1 snippet because we only want a single short clip.
            max_snippets=request.max_snippets or 1
        )
        snippets = snippets_response.snippets
        logger.info(f"Extracted {len(snippets)} snippets")
        
        # Step 2: Generate scenes
        scenes_response = await scene_generator.generate_scenes(snippets)
        scenes = scenes_response.scenes
        logger.info(f"Generated {len(scenes)} scenes")

        # We only want a single ~15s clip total.
        if not scenes:
            raise ValueError("No scenes generated")
        scenes = scenes[:1]
        scenes[0].duration = 15
        logger.info("Using 1 scene, targeting 15s duration")
        
        # Step 3: Generate videos
        videos_response = await veo_service.generate_videos(scenes)
        video_scenes = videos_response.video_scenes
        logger.info(f"Generated {len(video_scenes)} video clips")
        
        # VeoService.generate_videos returns a single extended video (final output),
        # so stitching is unnecessary (and can break across MoviePy versions).
        if not video_scenes:
            raise ValueError("No video scenes returned from Veo")
        final_video_path = video_scenes[0].file_path
        logger.info(f"Final silent video (from Veo): {final_video_path}")
        
        return VideoGenerationFullResponse(
            snippets=snippets,
            scenes=scenes,
            video_scenes=video_scenes,
            audio_scenes=[],
            stitched_video_path=None,
            final_video_path=final_video_path,
            total_duration=15
        )
        
    except Exception as e:
        logger.error(f"Error in full pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

