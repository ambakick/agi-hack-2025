# System Architecture

## Overview
This document describes the technical architecture of the AI-powered podcast generation system, including component structure, data flow, and integration patterns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Web UI)                        │
│                     React/Next.js (Optional)                     │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP/REST
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Python)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      API Layer (REST)                      │  │
│  │    /discovery  /transcription  /script  /audio  /video    │  │
│  └───────────────────────────────┬───────────────────────────┘  │
│                                  │                               │
│  ┌───────────────────────────────┴───────────────────────────┐  │
│  │                    Service Layer                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │ YouTube  │  │  Gemini  │  │ElevenLabs│  │   Veo    │  │  │
│  │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │  │
│  │  │Transcript│  │ Remotion │  │ShowNotes │                │  │
│  │  │ Service  │  │ Service  │  │ Service  │                │  │
│  │  └──────────┘  └──────────┘  └──────────┘                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      Data Layer                             │  │
│  │         Database (PostgreSQL/SQLite) + File Storage        │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ YouTube  │  │  Google  │  │ElevenLabs│  │  Google  │        │
│  │Data API  │  │ Gemini 3 │  │   API    │  │   Veo    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. API Layer (FastAPI)

**Responsibility**: Handle HTTP requests, validate input, route to services

**Structure**:
```
app/api/v1/
├── endpoints/
│   ├── discovery.py      # YouTube search endpoints
│   ├── references.py     # Reference selection
│   ├── transcription.py  # Transcript retrieval
│   ├── analysis.py       # Content analysis
│   ├── outline.py        # Outline generation
│   ├── script.py         # Script writing
│   ├── audio.py          # TTS generation
│   ├── video.py          # Video generation
│   ├── shownotes.py      # Show notes generation
│   └── episodes.py       # Episode management
└── deps.py               # Shared dependencies
```

**Key Patterns**:
- Pydantic models for request/response validation
- Dependency injection for services
- Async route handlers for I/O operations
- Proper HTTP status codes and error handling

**Example Endpoint**:
```python
@router.post("/generate", response_model=ScriptResponse)
async def generate_script(
    request: ScriptRequest,
    gemini_service: GeminiService = Depends(get_gemini_service),
    db: Session = Depends(get_db)
) -> ScriptResponse:
    # Validate input
    # Call service
    # Return response
    pass
```

### 2. Service Layer

**Responsibility**: Business logic, external API integration, orchestration

#### YouTube Service
- Search for podcasts by topic
- Retrieve video metadata
- Fetch captions/subtitles
- Handle API quotas and rate limits

```python
class YouTubeService:
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    async def search_podcasts(self, query: str, max_results: int = 10) -> List[Video]:
        """Search for podcast videos related to query."""
        pass

    async def get_transcript(self, video_id: str) -> str:
        """Retrieve transcript/captions for a video."""
        pass
```

#### Gemini Service
- Content analysis
- Outline generation
- Script writing
- Show notes generation
- Scene segmentation for video

```python
class GeminiService:
    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel('gemini-3-...')

    async def analyze_content(self, transcripts: List[str]) -> Analysis:
        """Analyze transcripts and extract themes."""
        pass

    async def generate_outline(self, analysis: Analysis, topic: str) -> Outline:
        """Create episode outline from analysis."""
        pass

    async def write_script(self, outline: Outline, analysis: Analysis) -> Script:
        """Generate full podcast script."""
        pass

    async def generate_show_notes(self, script: Script, timeline: Timeline) -> str:
        """Create show notes with timestamps."""
        pass

    async def segment_scenes(self, script: Script) -> List[ScenePrompt]:
        """Break script into visual scenes for Veo."""
        pass
```

#### ElevenLabs Service
- Text-to-speech conversion
- Voice management
- Audio file handling

```python
class ElevenLabsService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"

    async def text_to_speech(
        self,
        text: str,
        voice_id: str,
        settings: VoiceSettings
    ) -> bytes:
        """Convert text to speech audio."""
        pass

    async def list_voices(self) -> List[Voice]:
        """Get available voices."""
        pass
```

#### Veo Service
- Generate video clips from text prompts
- Handle Vertex AI integration
- Manage video file retrieval

```python
class VeoService:
    def __init__(self, project_id: str, location: str):
        self.client = aiplatform.VideoGenerationClient(...)

    async def generate_video(
        self,
        prompt: str,
        duration: float = 5.0,
        aspect_ratio: str = "9:16"
    ) -> VideoClip:
        """Generate video clip from text prompt."""
        pass
```

#### Remotion Service
- Orchestrate Remotion rendering
- Compose video from components
- Sync audio with video timeline

```python
class RemotionService:
    async def compose_video(
        self,
        scenes: List[VideoClip],
        audio_file: str,
        timeline: Timeline
    ) -> str:
        """Render final video using Remotion."""
        # Call Remotion CLI or API
        # Pass composition parameters
        # Return path to rendered video
        pass
```

### 3. Data Layer

**Responsibility**: Persist data, manage state, store files

#### Database Schema (PostgreSQL/SQLite)

```sql
-- Episodes table
CREATE TABLE episodes (
    id UUID PRIMARY KEY,
    topic TEXT NOT NULL,
    status VARCHAR(50),  -- 'processing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Reference videos
CREATE TABLE references (
    id UUID PRIMARY KEY,
    episode_id UUID REFERENCES episodes(id),
    video_id VARCHAR(255),
    title TEXT,
    channel TEXT,
    duration INTEGER,
    transcript TEXT
);

-- Generated content
CREATE TABLE content (
    id UUID PRIMARY KEY,
    episode_id UUID REFERENCES episodes(id),
    analysis JSONB,
    outline JSONB,
    script TEXT,
    show_notes TEXT
);

-- Media files
CREATE TABLE media_files (
    id UUID PRIMARY KEY,
    episode_id UUID REFERENCES episodes(id),
    type VARCHAR(50),  -- 'audio', 'video', 'veo_clip'
    file_path TEXT,
    file_size BIGINT,
    duration FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### File Storage
- Local filesystem or cloud storage (S3, GCS)
- Organized by episode ID
- Store audio, video, and Veo clips

```
storage/
├── episodes/
│   ├── {episode_id}/
│   │   ├── audio/
│   │   │   └── podcast.mp3
│   │   ├── video/
│   │   │   ├── veo_clips/
│   │   │   │   ├── scene_1.mp4
│   │   │   │   ├── scene_2.mp4
│   │   │   │   └── ...
│   │   │   └── final.mp4
│   │   └── metadata.json
```

### 4. Data Models (Pydantic)

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Video(BaseModel):
    video_id: str
    title: str
    channel: str
    duration: int
    thumbnail_url: str
    view_count: Optional[int]

class Transcript(BaseModel):
    video_id: str
    text: str
    language: str = "en"

class Analysis(BaseModel):
    themes: List[str]
    key_points: List[str]
    anecdotes: List[str]
    facts: List[str]

class OutlineSegment(BaseModel):
    title: str
    duration: float  # minutes
    key_points: List[str]

class Outline(BaseModel):
    introduction: OutlineSegment
    segments: List[OutlineSegment]
    conclusion: OutlineSegment

class Script(BaseModel):
    full_text: str
    segments: List[dict]  # {title, text, start_time}
    word_count: int
    estimated_duration: float  # minutes

class ScenePrompt(BaseModel):
    scene_number: int
    prompt: str
    duration: float  # seconds
    start_time: float

class VideoClip(BaseModel):
    scene_number: int
    file_path: str
    duration: float

class Episode(BaseModel):
    id: str
    topic: str
    status: str
    references: List[Video]
    analysis: Optional[Analysis]
    outline: Optional[Outline]
    script: Optional[Script]
    audio_url: Optional[str]
    video_url: Optional[str]
    show_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
```

## Module Dependencies

### Dependency Graph
```
discovery → transcription → analysis → outline → script
                                                    ↓
                                          ┌─────────┴─────────┐
                                          ↓                   ↓
                                    audio (TTS)         video (Veo+Remotion)
                                          ↓                   ↓
                                    show_notes          show_notes
                                          └─────────┬─────────┘
                                                    ↓
                                            final_assembly
```

### Service Dependencies
- **YouTubeService**: No dependencies
- **TranscriptionService**: Depends on YouTubeService
- **GeminiService**: No dependencies (standalone)
- **ElevenLabsService**: No dependencies
- **VeoService**: No dependencies
- **RemotionService**: Depends on VeoService (video clips)
- **ShowNotesService**: Depends on GeminiService

## Processing Pipeline

### Synchronous Steps (Sequential)
1. Discovery (YouTube search)
2. Reference selection (user input)
3. Transcription retrieval
4. Content analysis (Gemini)
5. Outline generation (Gemini)
6. User outline approval
7. Script writing (Gemini)

### Parallel Processing (Concurrent)
After script is finalized:
- Audio generation (ElevenLabs)
- Video scene segmentation (Gemini)
- Show notes generation (Gemini)

Then:
- Video clip generation (Veo) - can be parallelized per scene
- Final video composition (Remotion) - requires audio + clips

### Async Job Queue (Optional)
For long-running tasks:
- Use Celery or similar for background jobs
- Implement task status tracking
- Provide progress updates to frontend

```python
# Example async task structure
from celery import Celery

app = Celery('podcast_gen')

@app.task
def generate_full_episode(episode_id: str):
    # Run full pipeline
    # Update status in database
    # Store results
    pass
```

## Error Handling Strategy

### Levels of Error Handling

1. **API Layer**: Catch exceptions, return appropriate HTTP status codes
2. **Service Layer**: Retry logic, fallback strategies
3. **Data Layer**: Transaction management, rollback on failure

### Retry Strategy
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_external_api():
    # API call here
    pass
```

### Fallback Strategies
- YouTube captions unavailable → Skip video or use STT
- Gemini API failure → Retry with modified prompt or use backup model
- Veo generation failure → Use stock footage or simpler visuals
- ElevenLabs quota exceeded → Queue for later or use alternative TTS

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Log all API calls
logger.info(f"Calling YouTube API: search for '{query}'")

# Log errors with context
logger.error(f"Failed to generate script for episode {episode_id}", exc_info=True)
```

## Security Considerations

### API Key Management
- Store in environment variables (never in code)
- Use secret management service in production (AWS Secrets Manager, GCP Secret Manager)
- Rotate keys regularly

### Input Validation
- Validate all user input with Pydantic
- Sanitize file uploads
- Rate limit API endpoints

### Authentication (Future)
- JWT tokens for user authentication
- API key authentication for programmatic access

## Scalability Considerations

### Horizontal Scaling
- FastAPI is stateless, can scale horizontally
- Use load balancer (nginx, AWS ALB)
- Separate services for different components

### Caching
- Cache YouTube search results
- Cache Gemini responses for common queries
- Use Redis for distributed caching

### Asynchronous Processing
- Offload long-running tasks to background workers
- Use message queue (RabbitMQ, Redis) for task distribution

### Database Optimization
- Index frequently queried fields
- Use connection pooling
- Consider read replicas for heavy read loads

## Development vs Production

### Development
- SQLite database
- Local file storage
- Direct API calls (no queue)
- Simple error handling

### Production
- PostgreSQL database
- Cloud storage (S3/GCS)
- Celery + Redis for background jobs
- Comprehensive logging and monitoring
- Auto-scaling infrastructure

## Technology Choices Rationale

- **FastAPI**: Modern, fast, async support, automatic OpenAPI docs
- **Python**: Rich ecosystem for AI/ML, good library support
- **Pydantic**: Type-safe data validation
- **Gemini 3**: State-of-the-art reasoning, long context, multimodal
- **ElevenLabs**: Best-in-class natural TTS
- **Veo**: Cutting-edge video generation
- **Remotion**: Programmatic video composition, React-based
- **PostgreSQL**: Robust, JSON support, scalable

## Future Architecture Improvements

- Microservices architecture (separate services for each component)
- Event-driven architecture (Kafka, Pub/Sub)
- GraphQL API alongside REST
- Real-time status updates via WebSockets
- Kubernetes for orchestration
- Monitoring with Prometheus + Grafana
- Distributed tracing with OpenTelemetry
