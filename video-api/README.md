# Video Generation API

A standalone FastAPI service that processes transcripts into synchronized video-audio content using Google Veo 3.1 and ElevenLabs.

## Overview

This service extracts interesting snippets from transcripts, generates 8-second scene descriptions, creates silent videos with Veo 3.1, generates matching audio with ElevenLabs, stitches videos together, and synchronizes audio with video.

## Features

- **Snippet Extraction**: Uses Gemini 2.5 Flash to identify engaging segments from transcripts
- **Scene Generation**: Creates detailed 8-second visual descriptions optimized for Veo
- **Video Generation**: Generates silent video clips using Veo 3.1 (8 seconds max per clip)
- **Audio Generation**: Creates matching audio clips using ElevenLabs TTS
- **Video Stitching**: Concatenates multiple video clips into a single video
- **Audio Synchronization**: Perfectly syncs audio with video timeline

## Setup

### 1. Install Dependencies

```bash
cd video-api
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `video-api/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### 3. Run the Service

```bash
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`

## API Endpoints

### Individual Component Endpoints

#### Extract Snippets
```http
POST /api/v1/extract-snippets
Content-Type: application/json

{
  "transcript": "Your transcript text here...",
  "format": "plain"
}
```

#### Generate Scenes
```http
POST /api/v1/generate-scenes
Content-Type: application/json

{
  "snippets": [
    {
      "text": "Snippet text",
      "start_time": 0.0,
      "end_time": 8.0
    }
  ]
}
```

#### Generate Videos
```http
POST /api/v1/generate-videos
Content-Type: application/json

{
  "scenes": [
    {
      "scene_number": 1,
      "transcript_text": "Text for scene",
      "visual_prompt": "Cinematic lighting, photorealistic 4k...",
      "duration": 8.0
    }
  ]
}
```

#### Generate Audio
```http
POST /api/v1/generate-audio
Content-Type: application/json

{
  "scenes": [...],
  "voice_id": "optional_voice_id"
}
```

#### Stitch Videos
```http
POST /api/v1/stitch-videos
Content-Type: application/json

{
  "video_paths": ["path/to/video1.mp4", "path/to/video2.mp4"]
}
```

#### Add Audio
```http
POST /api/v1/add-audio
Content-Type: application/json

{
  "video_path": "path/to/video.mp4",
  "audio_path": "path/to/audio.mp3"
}
```

### Full Pipeline Endpoint

#### Generate Complete Video
```http
POST /api/v1/generate-video
Content-Type: application/json

{
  "transcript": "Your full transcript text...",
  "transcript_format": "plain",
  "voice_id": "optional_voice_id",
  "max_snippets": 5
}
```

This endpoint runs the complete pipeline:
1. Extract snippets
2. Generate scenes
3. Generate videos (Veo)
4. Generate audio (ElevenLabs)
5. Stitch videos
6. Sync audio

## Usage Examples

### Python Example

```python
import requests

# Full pipeline
response = requests.post(
    "http://localhost:8001/api/v1/generate-video",
    json={
        "transcript": "Your transcript here...",
        "transcript_format": "plain",
        "max_snippets": 5
    }
)

result = response.json()
print(f"Final video: {result['final_video_path']}")
```

### cURL Example

```bash
curl -X POST "http://localhost:8001/api/v1/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Your transcript text...",
    "transcript_format": "plain"
  }'
```

## Transcript Formats

### Plain Text
```json
{
  "transcript": "Full transcript as plain text...",
  "format": "plain"
}
```

### JSON with Timestamps
```json
{
  "transcript": [
    {
      "text": "Segment text",
      "start": 0.0,
      "duration": 5.0
    }
  ],
  "format": "json"
}
```

## Output Files

Generated files are saved in:
- Videos: `./video_output/` (configurable via `VIDEO_OUTPUT_DIR`)
- Audio: `./audio_output/` (configurable via `AUDIO_OUTPUT_DIR`)

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Configuration

Environment variables (see `.env.example`):

- `GEMINI_API_KEY`: Required - Google Gemini API key
- `ELEVENLABS_API_KEY`: Required - ElevenLabs API key
- `VIDEO_OUTPUT_DIR`: Output directory for videos (default: `./video_output`)
- `AUDIO_OUTPUT_DIR`: Output directory for audio (default: `./audio_output`)
- `MAX_SCENE_DURATION`: Maximum scene duration in seconds (default: 8)
- `PORT`: Server port (default: 8001)
- `DEBUG`: Enable debug mode (default: false)
- `CORS_ORIGINS`: Comma-separated CORS origins (default: `http://localhost:3000`)

## Architecture

```
Transcript Input
    ↓
Extract Snippets (Gemini 2.5 Flash)
    ↓
Generate Scene Descriptions (Gemini 2.5 Flash)
    ↓
    ├→ Generate Videos (Veo 3.1) - Silent clips
    └→ Generate Audio (ElevenLabs) - Matching clips
    ↓
Stitch Videos
    ↓
Sync Audio with Video
    ↓
Final Video with Audio
```

## Error Handling

The API includes comprehensive error handling:
- Invalid input validation
- API rate limit handling
- File I/O error handling
- Video processing error handling

All errors return appropriate HTTP status codes with descriptive error messages.

## Testing Individual Components

Each component can be tested independently:

1. **Test snippet extraction**: Use `/api/v1/extract-snippets`
2. **Test scene generation**: Use `/api/v1/generate-scenes`
3. **Test video generation**: Use `/api/v1/generate-videos`
4. **Test audio generation**: Use `/api/v1/generate-audio`
5. **Test video stitching**: Use `/api/v1/stitch-videos`
6. **Test audio sync**: Use `/api/v1/add-audio`

## Integration

This service is designed to be integrated with the main backend later. It can be:
- Imported as a module
- Added as a router to the main FastAPI app
- Run as a separate microservice

## Notes

- Veo 3.1 has a maximum duration of 8 seconds per video clip
- Video generation can take 30 seconds to several minutes per clip
- Audio generation is typically faster (a few seconds per clip)
- The service handles async operations and polling for Veo video generation

## License

MIT License - Built for Gemini AGI Hackathon December 2025

