"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class PodcastFormat(str, Enum):
    """Podcast format options."""
    SINGLE_HOST = "single_host"
    MULTI_HOST = "multi_host"


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

