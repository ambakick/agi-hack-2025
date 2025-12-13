"""Tests for audio service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
from app.services.audio_service import AudioService
from app.models.schemas import SceneDescription


@pytest.fixture
def sample_scene():
    """Sample scene for testing."""
    return SceneDescription(
        scene_number=1,
        transcript_text="AI is transforming the world.",
        visual_prompt="Test prompt",
        duration=8.0
    )


@pytest.mark.asyncio
async def test_generate_audio(sample_scene):
    """Test audio generation for a single scene."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('app.services.audio_service.ElevenLabs') as mock_elevenlabs:
            mock_client = Mock()
            mock_generator = iter([b'audio_chunk_1', b'audio_chunk_2', b'audio_chunk_3'])
            mock_client.text_to_speech = Mock()
            mock_client.text_to_speech.convert = Mock(return_value=mock_generator)
            mock_elevenlabs.return_value = mock_client
            
            service = AudioService(api_key="test_key")
            service.output_dir = tmpdir
            
            result = await service.generate_audio(sample_scene)
            
            assert result.scene_number == 1
            assert result.duration == 8.0
            assert result.transcript_text == sample_scene.transcript_text
            assert Path(result.file_path).exists()


@pytest.mark.asyncio
async def test_generate_audio_clips_multiple(sample_scenes):
    """Test audio generation for multiple scenes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('app.services.audio_service.ElevenLabs') as mock_elevenlabs:
            mock_client = Mock()
            mock_generator = iter([b'audio_chunk'])
            mock_client.text_to_speech = Mock()
            mock_client.text_to_speech.convert = Mock(return_value=mock_generator)
            mock_elevenlabs.return_value = mock_client
            
            service = AudioService(api_key="test_key")
            service.output_dir = tmpdir
            
            result = await service.generate_audio_clips(sample_scenes)
            
            assert len(result.audio_scenes) == len(sample_scenes)
            assert result.total_duration == sum(s.duration for s in sample_scenes)
            assert result.voice_id == AudioService.DEFAULT_VOICE_ID


@pytest.mark.asyncio
async def test_generate_audio_custom_voice(sample_scene):
    """Test audio generation with custom voice ID."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch('app.services.audio_service.ElevenLabs') as mock_elevenlabs:
            mock_client = Mock()
            mock_generator = iter([b'audio_chunk'])
            mock_client.text_to_speech = Mock()
            mock_client.text_to_speech.convert = Mock(return_value=mock_generator)
            mock_elevenlabs.return_value = mock_client
            
            service = AudioService(api_key="test_key")
            service.output_dir = tmpdir
            
            custom_voice_id = "custom_voice_123"
            result = await service.generate_audio(sample_scene, voice_id=custom_voice_id)
            
            # Verify custom voice was used
            mock_client.text_to_speech.convert.assert_called_once()
            call_args = mock_client.text_to_speech.convert.call_args
            assert call_args.kwargs['voice_id'] == custom_voice_id

