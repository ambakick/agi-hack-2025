"""Tests for Pydantic models."""

import pytest
from app.models.schemas import (
    TranscriptInput,
    TranscriptSegment,
    Snippet,
    SceneDescription,
    VideoScene,
    AudioScene,
    VideoGenerationRequest,
)


def test_transcript_input_plain_text():
    """Test TranscriptInput with plain text."""
    transcript = TranscriptInput(transcript="Hello world", format="plain")
    assert transcript.transcript == "Hello world"
    assert transcript.format == "plain"


def test_transcript_input_json():
    """Test TranscriptInput with JSON segments."""
    segments = [
        TranscriptSegment(text="Hello", start=0.0, duration=1.0),
        TranscriptSegment(text="World", start=1.0, duration=1.0),
    ]
    transcript = TranscriptInput(transcript=segments, format="json")
    assert len(transcript.transcript) == 2
    assert transcript.format == "json"


def test_snippet_model():
    """Test Snippet model."""
    snippet = Snippet(
        text="Test snippet",
        start_time=0.0,
        end_time=8.0,
        context="Test context",
        reason="Test reason"
    )
    assert snippet.text == "Test snippet"
    assert snippet.start_time == 0.0
    assert snippet.end_time == 8.0


def test_scene_description_model():
    """Test SceneDescription model."""
    scene = SceneDescription(
        scene_number=1,
        transcript_text="Test text",
        visual_prompt="Test prompt",
        duration=8.0,
        start_time=0.0
    )
    assert scene.scene_number == 1
    assert scene.duration == 8.0
    assert scene.visual_prompt == "Test prompt"


def test_video_scene_model():
    """Test VideoScene model."""
    video_scene = VideoScene(
        scene_number=1,
        file_path="/tmp/test.mp4",
        duration=8.0,
        transcript_text="Test"
    )
    assert video_scene.scene_number == 1
    assert video_scene.file_path == "/tmp/test.mp4"
    assert video_scene.duration == 8.0


def test_audio_scene_model():
    """Test AudioScene model."""
    audio_scene = AudioScene(
        scene_number=1,
        file_path="/tmp/test.mp3",
        duration=8.0,
        transcript_text="Test"
    )
    assert audio_scene.scene_number == 1
    assert audio_scene.file_path == "/tmp/test.mp3"
    assert audio_scene.duration == 8.0


def test_video_generation_request():
    """Test VideoGenerationRequest model."""
    request = VideoGenerationRequest(
        transcript="Test transcript",
        transcript_format="plain",
        voice_id="test_voice",
        max_snippets=5
    )
    assert request.transcript == "Test transcript"
    assert request.transcript_format == "plain"
    assert request.voice_id == "test_voice"
    assert request.max_snippets == 5

