"""Tests for Veo service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
from app.services.veo_service import VeoService
from app.models.schemas import SceneDescription


@pytest.fixture
def sample_scene():
    """Sample scene for testing."""
    return SceneDescription(
        scene_number=1,
        transcript_text="AI is transforming the world.",
        visual_prompt="Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio. Futuristic cityscape.",
        duration=8.0
    )


@pytest.mark.asyncio
async def test_generate_video(sample_scene):
    """Test video generation for a single scene."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('app.services.veo_service.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_operation = Mock()
            mock_operation.done = True
            mock_operation.response = Mock()
            mock_operation.response.generated_videos = [Mock()]
            mock_operation.response.generated_videos[0].video = Mock()
            
            mock_file = Mock()
            mock_file.save = Mock()
            mock_client.files.download = Mock(return_value=mock_file)
            mock_client.models.generate_videos = Mock(return_value=mock_operation)
            mock_client.operations.get = Mock(return_value=mock_operation)
            mock_client_class.return_value = mock_client
            
            service = VeoService(api_key="test_key")
            service.output_dir = tmpdir
            
            result = await service.generate_video(sample_scene)
            
            assert result.scene_number == 1
            assert result.duration == 8.0
            assert result.transcript_text == sample_scene.transcript_text
            assert Path(result.file_path).exists() or mock_file.save.called


@pytest.mark.asyncio
async def test_generate_videos_multiple(sample_scenes):
    """Test video generation for multiple scenes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('app.services.veo_service.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_operation = Mock()
            mock_operation.done = True
            mock_operation.response = Mock()
            mock_operation.response.generated_videos = [Mock()]
            mock_operation.response.generated_videos[0].video = Mock()
            
            mock_file = Mock()
            mock_file.save = Mock()
            mock_client.files.download = Mock(return_value=mock_file)
            mock_client.models.generate_videos = Mock(return_value=mock_operation)
            mock_client.operations.get = Mock(return_value=mock_operation)
            mock_client_class.return_value = mock_client
            
            service = VeoService(api_key="test_key")
            service.output_dir = tmpdir
            
            result = await service.generate_videos(sample_scenes)
            
            assert len(result.video_scenes) == len(sample_scenes)
            assert result.total_duration == sum(s.duration for s in sample_scenes)


def test_poll_operation_complete():
    """Test polling operation that's already complete."""
    with patch('app.services.veo_service.genai.Client') as mock_client_class:
        mock_client = Mock()
        mock_operation = Mock()
        mock_operation.done = True
        mock_client_class.return_value = mock_client
        
        service = VeoService(api_key="test_key")
        result = service._poll_operation(mock_operation)
        
        assert result.done is True

