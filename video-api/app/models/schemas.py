"""Pydantic models for video generation API."""

from typing import List, Optional, Union
from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    """A segment of transcript with timestamp."""
    text: str
    start: float = Field(..., description="Start time in seconds")
    duration: float = Field(..., description="Duration in seconds")


class TranscriptInput(BaseModel):
    """Input transcript in various formats."""
    transcript: Union[str, List[TranscriptSegment]] = Field(
        ...,
        description="Transcript as plain text or list of segments with timestamps"
    )
    format: str = Field(
        default="plain",
        description="Format: 'plain' for text, 'json' for timestamped segments"
    )


class Snippet(BaseModel):
    """An extracted interesting snippet from transcript."""
    text: str = Field(..., description="Snippet text")
    start_time: Optional[float] = Field(None, description="Start time in seconds")
    end_time: Optional[float] = Field(None, description="End time in seconds")
    context: Optional[str] = Field(None, description="Context around the snippet")
    reason: Optional[str] = Field(None, description="Why this snippet was selected")


class SnippetExtractionResponse(BaseModel):
    """Response from snippet extraction."""
    snippets: List[Snippet] = Field(..., description="Extracted snippets")
    total_snippets: int = Field(..., description="Total number of snippets")


class SceneDescription(BaseModel):
    """8-second scene description for Veo generation."""
    scene_number: int = Field(..., description="Scene sequence number")
    transcript_text: str = Field(..., description="Original transcript text for this scene")
    visual_prompt: str = Field(..., description="Detailed visual description for Veo")
    duration: float = Field(default=8.0, description="Scene duration in seconds")
    start_time: Optional[float] = Field(None, description="Start time in original transcript")


class SceneGenerationResponse(BaseModel):
    """Response from scene generation."""
    scenes: List[SceneDescription] = Field(..., description="Generated scene descriptions")
    total_duration: float = Field(..., description="Total duration in seconds")


class VideoScene(BaseModel):
    """Generated video clip metadata."""
    scene_number: int = Field(..., description="Scene sequence number")
    file_path: str = Field(..., description="Path to video file")
    duration: float = Field(..., description="Video duration in seconds")
    transcript_text: str = Field(..., description="Matching transcript text")


class VideoGenerationResponse(BaseModel):
    """Response from video generation."""
    video_scenes: List[VideoScene] = Field(..., description="Generated video clips")
    total_duration: float = Field(..., description="Total video duration")


class AudioScene(BaseModel):
    """Generated audio clip metadata."""
    scene_number: int = Field(..., description="Scene sequence number")
    file_path: str = Field(..., description="Path to audio file")
    duration: float = Field(..., description="Audio duration in seconds")
    transcript_text: str = Field(..., description="Matching transcript text")


class AudioGenerationResponse(BaseModel):
    """Response from audio generation."""
    audio_scenes: List[AudioScene] = Field(..., description="Generated audio clips")
    total_duration: float = Field(..., description="Total audio duration")
    voice_id: str = Field(..., description="Voice ID used")


class VideoStitchRequest(BaseModel):
    """Request to stitch videos."""
    video_paths: List[str] = Field(..., description="List of video file paths to stitch")
    output_path: Optional[str] = Field(None, description="Output file path")


class VideoStitchResponse(BaseModel):
    """Response from video stitching."""
    stitched_video_path: str = Field(..., description="Path to stitched video")
    duration: float = Field(..., description="Total duration")


class AudioSyncRequest(BaseModel):
    """Request to sync audio with video."""
    video_path: str = Field(..., description="Path to video file")
    audio_path: str = Field(..., description="Path to audio file")
    output_path: Optional[str] = Field(None, description="Output file path")


class AudioSyncResponse(BaseModel):
    """Response from audio synchronization."""
    final_video_path: str = Field(..., description="Path to final video with audio")
    duration: float = Field(..., description="Total duration")


class VideoGenerationRequest(BaseModel):
    """Full video generation request."""
    transcript: Union[str, List[TranscriptSegment]] = Field(
        ...,
        description="Transcript input"
    )
    transcript_format: str = Field(
        default="plain",
        description="Format: 'plain' or 'json'"
    )
    voice_id: Optional[str] = Field(
        None,
        description="ElevenLabs voice ID (optional, uses default if not provided)"
    )
    max_snippets: Optional[int] = Field(
        None,
        description="Maximum number of snippets to extract (optional)"
    )


class VideoGenerationFullResponse(BaseModel):
    """Full pipeline response."""
    snippets: List[Snippet] = Field(..., description="Extracted snippets")
    scenes: List[SceneDescription] = Field(..., description="Generated scenes")
    video_scenes: List[VideoScene] = Field(..., description="Generated video clips")
    audio_scenes: List[AudioScene] = Field(..., description="Generated audio clips")
    stitched_video_path: Optional[str] = Field(None, description="Stitched video path")
    final_video_path: str = Field(..., description="Final video with audio")
    total_duration: float = Field(..., description="Total duration in seconds")

