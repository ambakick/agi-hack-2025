# Test Suite

Comprehensive test suite for the Video Generation API service.

## Running Tests

### Run all tests
```bash
cd video-api
pytest
```

### Run specific test file
```bash
pytest tests/test_snippet_extractor.py
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_snippet_extractor.py` - Tests for snippet extraction service
- `test_scene_generator.py` - Tests for scene generation service
- `test_veo_service.py` - Tests for Veo video generation service
- `test_audio_service.py` - Tests for ElevenLabs audio service
- `test_video_utils.py` - Tests for utility functions
- `test_api_endpoints.py` - Tests for API endpoints
- `test_models.py` - Tests for Pydantic models

## Test Coverage

The test suite includes:
- Unit tests for each service
- Integration tests for API endpoints
- Mocked external API calls (Gemini, Veo, ElevenLabs)
- Model validation tests
- Error handling tests

## Notes

- External APIs are mocked to avoid actual API calls during testing
- Tests use temporary directories for file operations
- Async functions are tested using `pytest-asyncio`

