"""Tests for snippet extractor service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.snippet_extractor import SnippetExtractor
from app.models.schemas import TranscriptInput, TranscriptSegment


@pytest.mark.asyncio
async def test_extract_snippets_plain_text(sample_transcript_text, mock_gemini_response):
    """Test snippet extraction with plain text transcript."""
    with patch('app.services.snippet_extractor.genai.GenerativeModel') as mock_model_class:
        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_gemini_response)
        mock_model_class.return_value = mock_model
        
        extractor = SnippetExtractor(api_key="test_key")
        transcript_input = TranscriptInput(
            transcript=sample_transcript_text,
            format="plain"
        )
        
        result = await extractor.extract_snippets(transcript_input, max_snippets=5)
        
        assert result.total_snippets == 1
        assert len(result.snippets) == 1
        assert result.snippets[0].text == "AI is really transforming the world right now."
        mock_model.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_extract_snippets_json_format(sample_transcript_segments, mock_gemini_response):
    """Test snippet extraction with JSON format transcript."""
    with patch('app.services.snippet_extractor.genai.GenerativeModel') as mock_model_class:
        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_gemini_response)
        mock_model_class.return_value = mock_model
        
        extractor = SnippetExtractor(api_key="test_key")
        transcript_input = TranscriptInput(
            transcript=sample_transcript_segments,
            format="json"
        )
        
        result = await extractor.extract_snippets(transcript_input, max_snippets=5)
        
        assert result.total_snippets == 1
        assert len(result.snippets) == 1
        mock_model.generate_content.assert_called_once()


def test_parse_transcript_text_plain():
    """Test parsing plain text transcript."""
    extractor = SnippetExtractor(api_key="test_key")
    transcript_input = TranscriptInput(transcript="Hello world", format="plain")
    
    result = extractor._parse_transcript_text(transcript_input)
    assert result == "Hello world"


def test_parse_transcript_text_json(sample_transcript_segments):
    """Test parsing JSON format transcript."""
    extractor = SnippetExtractor(api_key="test_key")
    transcript_input = TranscriptInput(transcript=sample_transcript_segments, format="json")
    
    result = extractor._parse_transcript_text(transcript_input)
    assert "Welcome to the podcast" in result
    assert "Today we're talking about AI" in result


def test_parse_json_response_with_code_block():
    """Test parsing JSON response with code block."""
    extractor = SnippetExtractor(api_key="test_key")
    response_text = """
    ```json
    {"snippets": [{"text": "test"}]}
    ```
    """
    
    result = extractor._parse_json_response(response_text)
    assert "snippets" in result
    assert len(result["snippets"]) == 1


def test_parse_json_response_plain():
    """Test parsing plain JSON response."""
    extractor = SnippetExtractor(api_key="test_key")
    response_text = '{"snippets": [{"text": "test"}]}'
    
    result = extractor._parse_json_response(response_text)
    assert "snippets" in result


def test_parse_json_response_invalid():
    """Test parsing invalid JSON raises error."""
    extractor = SnippetExtractor(api_key="test_key")
    response_text = "not valid json"
    
    with pytest.raises(ValueError):
        extractor._parse_json_response(response_text)

