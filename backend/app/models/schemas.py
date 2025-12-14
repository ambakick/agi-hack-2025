"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any
from enum import Enum


class PodcastFormat(str, Enum):
    """Podcast format options."""
    SINGLE_HOST = "single"
    TWO_HOSTS = "two_hosts"


class SourceType(str, Enum):
    """Source type options for multi-modal input."""
    YOUTUBE = "youtube"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    PDF = "pdf"


class SourceMetadata(BaseModel):
    """Metadata for a source."""
    video_id: Optional[str] = None
    channel_name: Optional[str] = None
    duration: Optional[str] = None
    view_count: Optional[int] = None
    published_at: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    page_count: Optional[int] = None


class Source(BaseModel):
    """Universal source model for multi-modal inputs."""
    id: str
    type: SourceType
    name: str
    thumbnail_url: Optional[str] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    metadata: Optional[SourceMetadata] = None


class UploadResponse(BaseModel):
    """Response from file upload."""
    id: str
    type: SourceType
    name: str
    thumbnail_url: Optional[str] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    metadata: Optional[SourceMetadata] = None


class VideoInfo(BaseModel):
    """YouTube video information."""
    video_id: str
    title: str
    channel_name: str
    thumbnail_url: str
    duration: str
    view_count: int
    published_at: str
    description: str


class DiscoveryRequest(BaseModel):
    """Request for YouTube podcast discovery."""
    topic: str = Field(..., description="Topic to search for")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results to return")
    language: str = Field(default="en", description="Language code (default: en)")


class DiscoveryResponse(BaseModel):
    """Response from YouTube podcast discovery."""
    videos: List[VideoInfo]
    query: str


class TranscriptRequest(BaseModel):
    """Request for transcript retrieval."""
    video_ids: List[str] = Field(..., description="List of YouTube video IDs")


class VideoTranscript(BaseModel):
    """Transcript for a single video."""
    video_id: str
    title: str
    transcript: str
    language: str
    duration_seconds: float


class TranscriptResponse(BaseModel):
    """Response with video transcripts."""
    transcripts: List[VideoTranscript]


class AnalysisRequest(BaseModel):
    """Request for content analysis."""
    transcripts: List[VideoTranscript]
    topic: str


class ThemePoint(BaseModel):
    """A key theme or discussion point."""
    theme: str
    description: str
    sources: List[str]  # video IDs


class AnalysisResponse(BaseModel):
    """Response from content analysis."""
    themes: List[ThemePoint]
    key_anecdotes: List[str]
    summary: str


class OutlineSection(BaseModel):
    """A section in the podcast outline."""
    id: str
    title: str
    description: str
    duration_minutes: float
    key_points: List[str]


class OutlineRequest(BaseModel):
    """Request for outline generation."""
    analysis: AnalysisResponse
    topic: str
    format: PodcastFormat = PodcastFormat.SINGLE_HOST
    target_duration_minutes: int = Field(default=15, ge=5, le=60)


class OutlineResponse(BaseModel):
    """Response with generated outline."""
    sections: List[OutlineSection]
    total_duration_minutes: float
    format: PodcastFormat


class ScriptRequest(BaseModel):
    """Request for script generation."""
    outline: OutlineResponse
    topic: str
    format: PodcastFormat
    style_notes: Optional[str] = None


class ScriptSegment(BaseModel):
    """A segment of the podcast script."""
    section_id: str
    speaker: str  # "HOST_1" or "HOST_2" for multi-host
    text: str
    timestamp_seconds: float


class ScriptResponse(BaseModel):
    """Response with generated script."""
    segments: List[ScriptSegment]
    format: PodcastFormat
    total_duration_seconds: float
    full_script: str


class TTSRequest(BaseModel):
    """Request for text-to-speech conversion."""
    script: ScriptResponse
    voice_id_host1: Optional[str] = None
    voice_id_host2: Optional[str] = None


# Video Generation Schemas
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
    video_file: Optional[Any] = Field(None, description="GenAI file reference for video extension", exclude=True)


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
        description='ElevenLabs voice ID (optional). If omitted/blank/"default", the backend uses its default voice.'
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
    audio_scenes: List[AudioScene] = Field(default_factory=list, description="Generated audio clips (empty for video-only pipeline)")
    stitched_video_path: Optional[str] = Field(None, description="Stitched video path")
    final_video_path: str = Field(..., description="Final video path (silent unless audio is added separately)")
    total_duration: float = Field(..., description="Total duration in seconds")

