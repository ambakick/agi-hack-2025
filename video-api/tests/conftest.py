"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from app.models.schemas import (
    TranscriptInput,
    TranscriptSegment,
    Snippet,
    SceneDescription,
)


@pytest.fixture
def sample_transcript_text():
    """Sample transcript text for testing."""
    return """
    Person 1: Welcome to the podcast. Today we're talking about artificial intelligence.
    Person 2: Yeah, AI is really transforming the world right now.
    Person 1: Absolutely. One of the most interesting developments is large language models.
    Person 2: Those are fascinating. They can understand and generate human-like text.
    Person 1: Exactly. And they're being used in so many applications.
    """


@pytest.fixture
def sample_transcript_segments():
    """Sample transcript segments with timestamps."""
    return [
        TranscriptSegment(text="Welcome to the podcast.", start=0.0, duration=2.0),
        TranscriptSegment(text="Today we're talking about AI.", start=2.0, duration=3.0),
        TranscriptSegment(text="AI is transforming the world.", start=5.0, duration=3.0),
    ]


@pytest.fixture
def sample_snippets():
    """Sample extracted snippets."""
    return [
        Snippet(
            text="AI is really transforming the world right now.",
            start_time=5.0,
            end_time=8.0,
            context="Discussion about AI impact",
            reason="Key insight about AI transformation"
        ),
        Snippet(
            text="Large language models can understand and generate human-like text.",
            start_time=15.0,
            end_time=20.0,
            context="Technical discussion",
            reason="Important technical detail"
        ),
    ]


@pytest.fixture
def sample_scenes():
    """Sample scene descriptions."""
    return [
        SceneDescription(
            scene_number=1,
            transcript_text="AI is really transforming the world right now.",
            visual_prompt="Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio. Futuristic cityscape with AI-powered technologies.",
            duration=8.0,
            start_time=5.0
        ),
        SceneDescription(
            scene_number=2,
            transcript_text="Large language models can understand and generate human-like text.",
            visual_prompt="Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio. Abstract visualization of neural networks.",
            duration=8.0,
            start_time=15.0
        ),
    ]


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    mock_response = Mock()
    mock_response.text = """
    {
        "snippets": [
            {
                "text": "AI is really transforming the world right now.",
                "start_time": 5.0,
                "end_time": 8.0,
                "context": "Discussion about AI impact",
                "reason": "Key insight about AI transformation"
            }
        ]
    }
    """
    return mock_response


@pytest.fixture
def mock_gemini_model(mock_gemini_response):
    """Mock Gemini model."""
    mock_model = Mock()
    mock_model.generate_content = Mock(return_value=mock_gemini_response)
    return mock_model


@pytest.fixture
def mock_veo_operation():
    """Mock Veo operation."""
    mock_op = Mock()
    mock_op.done = True
    mock_op.response = Mock()
    mock_op.response.generated_videos = [Mock()]
    mock_op.response.generated_videos[0].video = Mock()
    return mock_op


@pytest.fixture
def mock_elevenlabs_client():
    """Mock ElevenLabs client."""
    mock_client = Mock()
    mock_generator = iter([b'audio_chunk_1', b'audio_chunk_2'])
    mock_client.text_to_speech = Mock()
    mock_client.text_to_speech.convert = Mock(return_value=mock_generator)
    return mock_client

