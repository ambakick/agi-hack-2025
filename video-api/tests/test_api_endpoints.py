"""Tests for API endpoints."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models.schemas import (
    TranscriptInput,
    Snippet,
    SceneDescription,
    SnippetExtractionResponse,
    SceneGenerationResponse,
    VideoGenerationResponse,
    AudioGenerationResponse,
)


@pytest.fixture
def client():
    """Test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_extract_snippets_endpoint(client, sample_transcript_text):
    """Test extract snippets endpoint."""
    mock_response = SnippetExtractionResponse(
        snippets=[
            Snippet(
                text="Test snippet",
                start_time=0.0,
                end_time=8.0
            )
        ],
        total_snippets=1
    )
    
    with patch('app.api.v1.video.snippet_extractor.extract_snippets', new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = mock_response
        
        response = client.post(
            "/api/v1/extract-snippets",
            json={
                "transcript": sample_transcript_text,
                "format": "plain"
            },
            params={"max_snippets": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_snippets"] == 1
        assert len(data["snippets"]) == 1


@pytest.mark.asyncio
async def test_generate_scenes_endpoint(client, sample_snippets):
    """Test generate scenes endpoint."""
    mock_response = SceneGenerationResponse(
        scenes=[
            SceneDescription(
                scene_number=1,
                transcript_text="Test",
                visual_prompt="Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio. Test scene.",
                duration=8.0
            )
        ],
        total_duration=8.0
    )
    
    with patch('app.api.v1.video.scene_generator.generate_scenes', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        response = client.post(
            "/api/v1/generate-scenes",
            json=[snippet.model_dump() for snippet in sample_snippets]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["scenes"]) == 1
        assert data["total_duration"] == 8.0


@pytest.mark.asyncio
async def test_generate_videos_endpoint(client, sample_scenes):
    """Test generate videos endpoint."""
    from app.models.schemas import VideoScene
    
    mock_response = VideoGenerationResponse(
        video_scenes=[
            VideoScene(
                scene_number=1,
                file_path="/tmp/test.mp4",
                duration=8.0,
                transcript_text="Test"
            )
        ],
        total_duration=8.0
    )
    
    with patch('app.api.v1.video.veo_service.generate_videos', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        response = client.post(
            "/api/v1/generate-videos",
            json=[scene.model_dump() for scene in sample_scenes]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["video_scenes"]) == 1


@pytest.mark.asyncio
async def test_generate_audio_endpoint(client, sample_scenes):
    """Test generate audio endpoint."""
    from app.models.schemas import AudioScene
    
    mock_response = AudioGenerationResponse(
        audio_scenes=[
            AudioScene(
                scene_number=1,
                file_path="/tmp/test.mp3",
                duration=8.0,
                transcript_text="Test"
            )
        ],
        total_duration=8.0,
        voice_id="test_voice"
    )
    
    with patch('app.api.v1.video.audio_service.generate_audio_clips', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = mock_response
        
        response = client.post(
            "/api/v1/generate-audio",
            json=[scene.model_dump() for scene in sample_scenes]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["audio_scenes"]) == 1


@pytest.mark.asyncio
async def test_generate_video_full_pipeline(client, sample_transcript_text):
    """Test full pipeline endpoint."""
    from app.models.schemas import (
        VideoScene,
        AudioScene,
        VideoGenerationFullResponse
    )
    
    mock_full_response = VideoGenerationFullResponse(
        snippets=[Snippet(text="Test", start_time=0.0, end_time=8.0)],
        scenes=[SceneDescription(
            scene_number=1,
            transcript_text="Test",
            visual_prompt="Test prompt",
            duration=8.0
        )],
        video_scenes=[VideoScene(
            scene_number=1,
            file_path="/tmp/video.mp4",
            duration=8.0,
            transcript_text="Test"
        )],
        audio_scenes=[AudioScene(
            scene_number=1,
            file_path="/tmp/audio.mp3",
            duration=8.0,
            transcript_text="Test"
        )],
        stitched_video_path="/tmp/stitched.mp4",
        final_video_path="/tmp/final.mp4",
        total_duration=8.0
    )
    
    with patch('app.api.v1.video.snippet_extractor.extract_snippets', new_callable=AsyncMock) as mock_extract, \
         patch('app.api.v1.video.scene_generator.generate_scenes', new_callable=AsyncMock) as mock_scenes, \
         patch('app.api.v1.video.veo_service.generate_videos', new_callable=AsyncMock) as mock_videos, \
         patch('app.api.v1.video.audio_service.generate_audio_clips', new_callable=AsyncMock) as mock_audio, \
         patch('app.api.v1.video.video_stitcher.stitch_videos', new_callable=AsyncMock) as mock_stitch, \
         patch('app.api.v1.video.audio_sync.sync_multiple_audio', new_callable=AsyncMock) as mock_sync:
        
        # Set up mocks
        mock_extract.return_value = SnippetExtractionResponse(
            snippets=mock_full_response.snippets,
            total_snippets=1
        )
        mock_scenes.return_value = SceneGenerationResponse(
            scenes=mock_full_response.scenes,
            total_duration=8.0
        )
        mock_videos.return_value = VideoGenerationResponse(
            video_scenes=mock_full_response.video_scenes,
            total_duration=8.0
        )
        mock_audio.return_value = AudioGenerationResponse(
            audio_scenes=mock_full_response.audio_scenes,
            total_duration=8.0,
            voice_id="test"
        )
        from app.models.schemas import VideoStitchResponse, AudioSyncResponse
        mock_stitch.return_value = VideoStitchResponse(
            stitched_video_path=mock_full_response.stitched_video_path,
            duration=8.0
        )
        mock_sync.return_value = AudioSyncResponse(
            final_video_path=mock_full_response.final_video_path,
            duration=8.0
        )
        
        response = client.post(
            "/api/v1/generate-video",
            json={
                "transcript": sample_transcript_text,
                "transcript_format": "plain",
                "max_snippets": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "final_video_path" in data
        assert "snippets" in data
        assert "scenes" in data

