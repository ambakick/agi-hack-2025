"""Video generation API endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List
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
from app.services.audio_service import AudioService
from app.services.video_stitcher import VideoStitcher
from app.services.audio_sync import AudioSync

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
snippet_extractor = SnippetExtractor(settings.gemini_api_key)
scene_generator = SceneGenerator(settings.gemini_api_key)
veo_service = VeoService(settings.gemini_api_key)
audio_service = AudioService(settings.elevenlabs_api_key)
video_stitcher = VideoStitcher()
audio_sync = AudioSync()


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
    voice_id: str = None
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
        result = await audio_service.generate_audio_clips(scenes, voice_id=voice_id)
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
    Full pipeline: Extract snippets, generate scenes, create videos and audio, stitch, and sync.
    
    Args:
        request: VideoGenerationRequest with transcript
        
    Returns:
        VideoGenerationFullResponse with complete pipeline results
    """
    try:
        logger.info("Starting full video generation pipeline...")
        
        # Step 1: Extract snippets
        transcript_input = TranscriptInput(
            transcript=request.transcript,
            format=request.transcript_format
        )
        snippets_response = await snippet_extractor.extract_snippets(
            transcript_input,
            max_snippets=request.max_snippets or 5
        )
        snippets = snippets_response.snippets
        logger.info(f"Extracted {len(snippets)} snippets")
        
        # Step 2: Generate scenes
        scenes_response = await scene_generator.generate_scenes(snippets)
        scenes = scenes_response.scenes
        logger.info(f"Generated {len(scenes)} scenes")
        
        # Step 3: Generate videos (parallel with audio)
        videos_response = await veo_service.generate_videos(scenes)
        video_scenes = videos_response.video_scenes
        logger.info(f"Generated {len(video_scenes)} video clips")
        
        # Step 4: Generate audio
        audio_response = await audio_service.generate_audio_clips(
            scenes,
            voice_id=request.voice_id
        )
        audio_scenes = audio_response.audio_scenes
        logger.info(f"Generated {len(audio_scenes)} audio clips")
        
        # Step 5: Stitch videos
        video_paths = [vs.file_path for vs in video_scenes]
        stitched_response = await video_stitcher.stitch_videos(video_paths)
        stitched_video_path = stitched_response.stitched_video_path
        logger.info(f"Stitched videos: {stitched_video_path}")
        
        # Step 6: Combine audio clips and sync with video
        audio_paths = [as_.file_path for as_ in audio_scenes]
        final_response = await audio_sync.sync_multiple_audio(
            stitched_video_path,
            audio_paths
        )
        final_video_path = final_response.final_video_path
        logger.info(f"Final video with audio: {final_video_path}")
        
        return VideoGenerationFullResponse(
            snippets=snippets,
            scenes=scenes,
            video_scenes=video_scenes,
            audio_scenes=audio_scenes,
            stitched_video_path=stitched_video_path,
            final_video_path=final_video_path,
            total_duration=final_response.duration
        )
        
    except Exception as e:
        logger.error(f"Error in full pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

