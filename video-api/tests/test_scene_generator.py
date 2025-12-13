"""Tests for scene generator service."""

import pytest
from unittest.mock import Mock, patch
from app.services.scene_generator import SceneGenerator
from app.models.schemas import Snippet


@pytest.mark.asyncio
async def test_generate_scenes(sample_snippets):
    """Test scene generation from snippets."""
    mock_response = Mock()
    mock_response.text = """
    {
        "scenes": [
            {
                "scene_number": 1,
                "transcript_text": "AI is really transforming the world right now.",
                "visual_prompt": "Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio. Futuristic cityscape.",
                "duration": 8.0,
                "start_time": 5.0
            }
        ]
    }
    """
    
    with patch('app.services.scene_generator.genai.GenerativeModel') as mock_model_class:
        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)
        mock_model_class.return_value = mock_model
        
        generator = SceneGenerator(api_key="test_key")
        result = await generator.generate_scenes(sample_snippets)
        
        assert len(result.scenes) == 1
        assert result.scenes[0].scene_number == 1
        assert result.scenes[0].duration == 8.0
        assert "Cinematic lighting" in result.scenes[0].visual_prompt
        assert result.total_duration == 8.0
        mock_model.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_scenes_multiple(sample_snippets):
    """Test scene generation with multiple snippets."""
    mock_response = Mock()
    mock_response.text = """
    {
        "scenes": [
            {
                "scene_number": 1,
                "transcript_text": "AI is really transforming the world right now.",
                "visual_prompt": "Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio. Scene 1.",
                "duration": 8.0,
                "start_time": 5.0
            },
            {
                "scene_number": 2,
                "transcript_text": "Large language models can understand and generate human-like text.",
                "visual_prompt": "Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio. Scene 2.",
                "duration": 8.0,
                "start_time": 15.0
            }
        ]
    }
    """
    
    with patch('app.services.scene_generator.genai.GenerativeModel') as mock_model_class:
        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)
        mock_model_class.return_value = mock_model
        
        generator = SceneGenerator(api_key="test_key")
        result = await generator.generate_scenes(sample_snippets)
        
        assert len(result.scenes) == 2
        assert result.total_duration == 16.0
        assert all(scene.duration == 8.0 for scene in result.scenes)


def test_parse_json_response_with_code_block():
    """Test parsing JSON response with code block."""
    generator = SceneGenerator(api_key="test_key")
    response_text = """
    ```json
    {"scenes": [{"scene_number": 1, "transcript_text": "test", "visual_prompt": "test", "duration": 8.0}]}
    ```
    """
    
    result = generator._parse_json_response(response_text)
    assert "scenes" in result
    assert len(result["scenes"]) == 1

