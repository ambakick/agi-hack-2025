# API Integration Guide

This document provides detailed information about integrating with external APIs used in the podcast generation system.

---

## YouTube Data API v3

### Overview
Used for discovering podcast content and retrieving transcripts.

### Setup
1. Create a Google Cloud Project: https://console.cloud.google.com
2. Enable YouTube Data API v3
3. Create API credentials (API Key)
4. Set quota limits (default: 10,000 units/day)

### Authentication
```python
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY')
```

### Key Endpoints

#### 1. Search for Videos
**Endpoint**: `youtube.search().list()`

**Use Case**: Discover podcast episodes by topic

**Parameters**:
```python
request = youtube.search().list(
    part="snippet",
    q="artificial intelligence podcast",  # Search query
    type="video",
    relevanceLanguage="en",  # English only
    maxResults=10,
    order="relevance",  # or "viewCount", "date"
    videoDuration="long"  # For podcast-length content
)
response = request.execute()
```

**Response Structure**:
```json
{
  "items": [
    {
      "id": {"videoId": "dQw4w9WgXcQ"},
      "snippet": {
        "title": "AI Podcast Episode",
        "channelTitle": "Tech Talks",
        "description": "...",
        "thumbnails": {"default": {"url": "..."}},
        "publishedAt": "2024-01-01T00:00:00Z"
      }
    }
  ]
}
```

**Quota Cost**: 100 units per request

#### 2. Get Video Details
**Endpoint**: `youtube.videos().list()`

**Use Case**: Retrieve metadata for selected videos

```python
request = youtube.videos().list(
    part="snippet,contentDetails,statistics",
    id="video_id_1,video_id_2"  # Comma-separated
)
response = request.execute()
```

**Response Includes**:
- Duration (ISO 8601 format: PT1H30M)
- View count, like count
- Full description

**Quota Cost**: 1 unit per request

#### 3. List Captions
**Endpoint**: `youtube.captions().list()`

**Use Case**: Check if captions are available

```python
request = youtube.captions().list(
    part="snippet",
    videoId="dQw4w9WgXcQ"
)
response = request.execute()
```

**Response**:
```json
{
  "items": [
    {
      "id": "caption_track_id",
      "snippet": {
        "language": "en",
        "trackKind": "standard",  # or "ASR" for auto-generated
        "isAutoSynced": true
      }
    }
  ]
}
```

**Quota Cost**: 50 units

#### 4. Download Captions
**Endpoint**: `youtube.captions().download()`

**Use Case**: Retrieve transcript text

```python
request = youtube.captions().download(
    id="caption_track_id",
    tfmt="srt"  # or "vtt"
)
caption_text = request.execute()
```

**Note**: Requires OAuth 2.0 authentication (not API key)

**Alternative**: Use `youtube_transcript_api` library (unofficial):
```python
from youtube_transcript_api import YouTubeTranscriptApi

transcript = YouTubeTranscriptApi.get_transcript('video_id')
# Returns: [{'text': '...', 'start': 0.0, 'duration': 2.5}, ...]
```

### Quota Management
- Daily quota: 10,000 units (default)
- Request quota increase if needed
- Cache search results to reduce API calls
- Monitor usage: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas

### Error Handling
```python
from googleapiclient.errors import HttpError

try:
    response = youtube.search().list(...).execute()
except HttpError as e:
    if e.resp.status == 403:
        # Quota exceeded or forbidden
        logger.error("YouTube API quota exceeded")
    elif e.resp.status == 404:
        # Video not found
        pass
```

### Rate Limiting Best Practices
- Implement exponential backoff
- Batch video ID requests when possible
- Use ETags for caching responses

---

## Google Gemini API

### Overview
Used for content analysis, outline generation, script writing, and show notes.

### Setup
**Option 1: AI Studio (Simpler)**
1. Get API key from https://ai.google.dev/
2. Use `google-generativeai` library

**Option 2: Vertex AI (Production)**
1. Enable Vertex AI in Google Cloud
2. Set up authentication (Service Account)
3. Use `google-cloud-aiplatform` library

### Authentication

**AI Studio**:
```python
import google.generativeai as genai

genai.configure(api_key='YOUR_API_KEY')
model = genai.GenerativeModel('gemini-1.5-pro')
```

**Vertex AI**:
```python
from vertexai.generative_models import GenerativeModel
import vertexai

vertexai.init(project='your-project', location='us-central1')
model = GenerativeModel('gemini-1.5-pro')
```

### Available Models
- `gemini-1.5-pro`: Best for complex reasoning, long context (2M tokens)
- `gemini-1.5-flash`: Faster, good for most tasks
- `gemini-2.0-flash-exp`: Latest experimental model (as of Dec 2024)

### Usage Patterns

#### 1. Content Analysis
```python
prompt = f"""
Analyze these podcast transcripts and extract key information.

Transcripts:
{transcripts_text}

Extract:
1. Main themes (3-5 topics)
2. Key discussion points for each theme
3. Interesting stories or anecdotes
4. Notable facts or statistics

Output as JSON:
{{
  "themes": ["theme1", "theme2"],
  "key_points": {{"theme1": ["point1", "point2"]}},
  "anecdotes": ["story1"],
  "facts": ["fact1"]
}}
"""

response = model.generate_content(prompt)
analysis = json.loads(response.text)
```

#### 2. Outline Generation
```python
prompt = f"""
Create a podcast episode outline for a 10-12 minute episode.

Topic: {topic}
Key themes: {themes}
Target audience: General tech enthusiasts

Structure:
- Introduction (30 seconds)
- 3-4 main segments (2-3 minutes each)
- Conclusion (30 seconds)

For each segment, include:
- Title
- Key points to cover
- Estimated duration

Output as JSON.
"""

response = model.generate_content(prompt)
```

#### 3. Script Writing
```python
prompt = f"""
Write a complete podcast script based on this outline.

Outline:
{outline_json}

Requirements:
- Conversational, engaging tone
- Natural spoken language
- Smooth transitions between segments
- Include an attention-grabbing intro
- Total length: 2000-2500 words
- Style: Single narrator (professional but friendly)

Format the output as plain text script.
"""

generation_config = {
    "temperature": 0.9,  # Creative
    "top_p": 0.95,
    "max_output_tokens": 8192,
}

response = model.generate_content(
    prompt,
    generation_config=generation_config
)
script = response.text
```

#### 4. Show Notes Generation
```python
prompt = f"""
Generate show notes for this podcast episode.

Script:
{script}

Timeline:
{timeline_json}

Include:
1. Episode summary (2-3 paragraphs)
2. Timestamped list of topics (format: MM:SS - Topic name)
3. Key takeaways (3-5 bullet points)

Format as Markdown.
"""

response = model.generate_content(prompt)
show_notes = response.text
```

#### 5. Video Scene Segmentation
```python
prompt = f"""
Break this podcast script into 5-6 visual scenes for video generation.

Script:
{script}

For each scene:
- Scene number
- Duration (approximately 5 seconds each)
- Start time in script
- Detailed text-to-video prompt

Each video prompt should:
- Start with: "Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio"
- Describe visual content that matches the script segment
- Be specific and cinematic

Output as JSON array.
"""

response = model.generate_content(prompt)
scenes = json.loads(response.text)
```

### Advanced Features

#### Streaming Responses
```python
response = model.generate_content(prompt, stream=True)
for chunk in response:
    print(chunk.text, end='')
```

#### Function Calling (for structured output)
```python
from google.generativeai.types import FunctionDeclaration, Tool

analyze_function = FunctionDeclaration(
    name="analyze_content",
    description="Analyze podcast transcripts",
    parameters={
        "type": "object",
        "properties": {
            "themes": {"type": "array", "items": {"type": "string"}},
            "key_points": {"type": "object"}
        }
    }
)

tool = Tool(function_declarations=[analyze_function])
model = genai.GenerativeModel('gemini-1.5-pro', tools=[tool])
```

#### Grounding (for fact-checking)
```python
# With Google Search grounding
from vertexai.preview.generative_models import grounding

tool = grounding.GoogleSearchRetrieval()
response = model.generate_content(
    prompt,
    tools=[tool]
)
```

### Rate Limits & Quotas
- **AI Studio**: Free tier has rate limits (varies)
- **Vertex AI**: Pay-per-token, higher limits
- Implement request throttling
- Handle `429 Too Many Requests` errors

### Error Handling
```python
try:
    response = model.generate_content(prompt)
except Exception as e:
    if "429" in str(e):
        # Rate limit - implement backoff
        time.sleep(60)
        retry()
    elif "400" in str(e):
        # Bad request - check prompt
        logger.error(f"Invalid prompt: {e}")
```

### Cost Optimization
- Use `gemini-1.5-flash` for simpler tasks
- Cache common prompts
- Limit output tokens: `max_output_tokens`
- Monitor usage in Cloud Console

---

## ElevenLabs API

### Overview
Text-to-speech service for generating podcast narration.

### Setup
1. Sign up at https://elevenlabs.io
2. Get API key from dashboard
3. Choose subscription plan (free tier available)

### Authentication
```python
import requests

ELEVENLABS_API_KEY = "your_api_key"
headers = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}
```

### Key Endpoints

#### 1. List Available Voices
**Endpoint**: `GET https://api.elevenlabs.io/v1/voices`

```python
response = requests.get(
    "https://api.elevenlabs.io/v1/voices",
    headers={"xi-api-key": ELEVENLABS_API_KEY}
)
voices = response.json()['voices']

# Example voice structure:
# {
#   "voice_id": "21m00Tcm4TlvDq8ikWAM",
#   "name": "Rachel",
#   "category": "premade",
#   "labels": {"accent": "american", "age": "young"}
# }
```

**Popular Voices**:
- Rachel: Professional, versatile
- Adam: Deep, authoritative
- Antoni: Well-rounded, friendly
- Bella: Soft, calming

#### 2. Text-to-Speech Conversion
**Endpoint**: `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`

```python
voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel

data = {
    "text": "Your podcast script here...",
    "model_id": "eleven_monolingual_v1",  # or "eleven_multilingual_v2"
    "voice_settings": {
        "stability": 0.5,  # 0-1, higher = more consistent
        "similarity_boost": 0.75,  # 0-1, higher = more like original voice
        "style": 0.0,  # 0-1, for v2 models
        "use_speaker_boost": True
    }
}

response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers=headers,
    json=data
)

# Save audio
with open("output.mp3", "wb") as f:
    f.write(response.content)
```

#### 3. Streaming Audio
```python
response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream",
    headers=headers,
    json=data,
    stream=True
)

with open("output.mp3", "wb") as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            f.write(chunk)
```

### Voice Settings Tuning

- **Stability** (0-1):
  - Low (0-0.4): More expressive, variable
  - Mid (0.5-0.7): Balanced
  - High (0.8-1.0): Consistent, less emotional

- **Similarity Boost** (0-1):
  - Low: More generic
  - High: Closer to original voice sample

- **Style** (v2 models only, 0-1):
  - Controls stylistic variation

### Character Limits
- **Free tier**: ~10,000 characters/month
- **Starter**: ~30,000 characters/month
- **Creator**: ~100,000 characters/month
- **Pro**: ~500,000 characters/month

**Strategy for long scripts**:
```python
def split_script(script: str, max_chars: int = 5000) -> List[str]:
    """Split script at sentence boundaries."""
    sentences = script.split('. ')
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

async def generate_audio_segments(script: str) -> List[bytes]:
    chunks = split_script(script)
    audio_segments = []

    for chunk in chunks:
        audio = await text_to_speech(chunk, voice_id)
        audio_segments.append(audio)

    return audio_segments
```

### Concatenating Audio Files
```python
from pydub import AudioSegment

def concatenate_audio(segments: List[str], output_path: str):
    """Merge multiple audio files into one."""
    combined = AudioSegment.empty()

    for segment_path in segments:
        audio = AudioSegment.from_mp3(segment_path)
        combined += audio

    combined.export(output_path, format="mp3")
```

### Error Handling
```python
response = requests.post(url, headers=headers, json=data)

if response.status_code == 401:
    # Invalid API key
    raise Exception("Invalid ElevenLabs API key")
elif response.status_code == 422:
    # Validation error (text too long, invalid voice_id)
    raise Exception(f"Invalid request: {response.json()}")
elif response.status_code == 429:
    # Rate limit / quota exceeded
    raise Exception("ElevenLabs quota exceeded")
```

### Rate Limiting
- Free tier: 3 requests/second
- Paid tiers: Higher limits
- Implement request queuing for multiple segments

---

## Google Veo (Video Generation)

### Overview
State-of-the-art text-to-video generation model from Google DeepMind.

### Setup
**Access via Vertex AI**:
1. Enable Vertex AI API in Google Cloud
2. Request access to Veo (may require allowlist)
3. Use `google-cloud-aiplatform` library

**Alternative: VideoFX** (https://videofx.google.com)
- Web interface for testing
- API access may be limited

### Authentication
```python
from google.cloud import aiplatform
import vertexai

vertexai.init(project='your-project-id', location='us-central1')
```

### Generating Video

```python
from vertexai.preview.vision_models import VideoGenerationModel

model = VideoGenerationModel.from_pretrained("veo-001")

prompt = """
Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio.
A futuristic cityscape at dawn with autonomous vehicles smoothly flowing through streets.
Camera slowly pans across the scene. Professional commercial quality.
"""

response = model.generate_video(
    prompt=prompt,
    aspect_ratio="9:16",  # Vertical for social media
    duration=5,  # seconds
    # Additional parameters may be available
)

# Download video
video_url = response.video_url
# Or get video bytes
video_bytes = response.video_bytes
```

### Prompt Engineering for Veo

**Best Practices**:
1. Always specify aspect ratio and quality
2. Be descriptive about visual elements
3. Include camera movements
4. Mention lighting and style

**Template**:
```
Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio.
[Main subject and action].
[Camera movement].
[Style/mood].
Professional commercial quality.
```

**Examples**:
```
# Tech scene
Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio.
Abstract visualization of neural networks with glowing blue nodes and flowing data streams.
Camera slowly rotates around the network structure.
Futuristic, high-tech aesthetic.
Professional commercial quality.

# Nature scene
Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio.
Lush green forest with sunlight streaming through trees, mist rising from the ground.
Camera tracks forward along a forest path.
Serene, peaceful atmosphere.
Professional commercial quality.

# Urban scene
Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio.
Busy city intersection at night with neon lights and people crossing streets.
Camera pans left to right capturing the urban energy.
Cyberpunk aesthetic with vibrant colors.
Professional commercial quality.
```

### Scene Segmentation Strategy
```python
async def generate_veo_scenes(scenes: List[ScenePrompt]) -> List[VideoClip]:
    """Generate video clips for each scene."""
    video_clips = []

    for scene in scenes:
        try:
            response = await model.generate_video(
                prompt=scene.prompt,
                aspect_ratio="9:16",
                duration=scene.duration
            )

            # Save video clip
            clip_path = f"scene_{scene.scene_number}.mp4"
            with open(clip_path, "wb") as f:
                f.write(response.video_bytes)

            video_clips.append(VideoClip(
                scene_number=scene.scene_number,
                file_path=clip_path,
                duration=scene.duration
            ))

        except Exception as e:
            logger.error(f"Failed to generate scene {scene.scene_number}: {e}")
            # Consider fallback strategy

    return video_clips
```

### Rate Limits & Quotas
- Veo is in preview/limited access
- Generation can take 30 seconds to several minutes per clip
- Implement async processing and status tracking
- Consider request quotas (TBD based on your access tier)

### Error Handling
```python
try:
    response = model.generate_video(prompt=prompt, aspect_ratio="9:16")
except Exception as e:
    # Handle various errors
    if "quota" in str(e).lower():
        logger.error("Veo quota exceeded")
    elif "access" in str(e).lower():
        logger.error("Veo access denied - check allowlist status")
    else:
        logger.error(f"Veo generation failed: {e}")
```

### Fallback Strategy
If Veo is unavailable:
- Use stock footage libraries (Pexels API, Unsplash)
- Generate simple animated backgrounds with Remotion
- Use static images with ken burns effect

---

## Remotion (Video Composition)

### Overview
Programmatic video creation using React. Allows precise synchronization of audio and visuals.

### Setup
```bash
npm install remotion
# or
pip install remotion  # If Python wrapper exists
```

### Basic Concept
Define video as React components, render programmatically.

### Project Structure
```
remotion-project/
├── src/
│   ├── Composition.tsx       # Main composition
│   ├── scenes/
│   │   ├── IntroScene.tsx
│   │   ├── VeoClipScene.tsx
│   │   └── OutroScene.tsx
│   └── index.ts
├── public/
│   ├── audio/
│   │   └── podcast.mp3
│   └── video/
│       └── veo_clips/
└── remotion.config.ts
```

### Example Composition
```typescript
import { Composition } from 'remotion';
import { PodcastVideo } from './PodcastVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PodcastEpisode"
        component={PodcastVideo}
        durationInFrames={3600}  // 60 seconds at 60fps
        fps={60}
        width={1080}
        height={1920}  // 9:16 aspect ratio
        defaultProps={{
          audioPath: '/audio/podcast.mp3',
          scenes: [/* scene data */]
        }}
      />
    </>
  );
};
```

### Scene Component
```typescript
import { useCurrentFrame, useVideoConfig, Video, Audio } from 'remotion';

export const PodcastVideo: React.FC<{
  audioPath: string;
  scenes: SceneData[];
}> = ({ audioPath, scenes }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div style={{ flex: 1, backgroundColor: '#000' }}>
      {/* Background audio */}
      <Audio src={audioPath} />

      {/* Video scenes */}
      {scenes.map((scene, index) => {
        const startFrame = scene.startTime * fps;
        const endFrame = startFrame + (scene.duration * fps);

        if (frame >= startFrame && frame < endFrame) {
          return (
            <Video
              key={index}
              src={scene.videoPath}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          );
        }
        return null;
      })}

      {/* Text overlays */}
      {/* ... */}
    </div>
  );
};
```

### Rendering from Python
```python
import subprocess
import json

def render_remotion_video(
    composition_id: str,
    props: dict,
    output_path: str
) -> str:
    """Render Remotion composition via CLI."""

    # Write props to file
    props_file = "props.json"
    with open(props_file, "w") as f:
        json.dump(props, f)

    # Render command
    command = [
        "npx", "remotion", "render",
        composition_id,
        output_path,
        "--props", props_file
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Remotion render failed: {result.stderr}")

    return output_path
```

### Alternative: Use Remotion Lambda
Cloud-based rendering for faster processing:
```python
# Deploy to AWS Lambda
subprocess.run(["npx", "remotion", "lambda", "deploy"])

# Render on Lambda
subprocess.run([
    "npx", "remotion", "lambda", "render",
    composition_id,
    "--props", props_file
])
```

---

## Summary: API Integration Checklist

### Before Development
- [ ] Create Google Cloud project
- [ ] Enable YouTube Data API v3
- [ ] Get YouTube API key
- [ ] Get Google Gemini API key (AI Studio or Vertex AI)
- [ ] Sign up for ElevenLabs, get API key
- [ ] Request Veo access (Vertex AI)
- [ ] Install Remotion
- [ ] Set up environment variables

### Environment Variables
```bash
# .env file
YOUTUBE_API_KEY=your_youtube_key
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# For Vertex AI
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Testing APIs
Create a test script to verify all integrations:
```python
# test_apis.py
async def test_all_apis():
    # Test YouTube
    videos = await youtube_service.search_podcasts("AI")
    print(f"✓ YouTube: Found {len(videos)} videos")

    # Test Gemini
    response = await gemini_service.test_connection()
    print("✓ Gemini: Connected")

    # Test ElevenLabs
    audio = await elevenlabs_service.text_to_speech("Test", voice_id)
    print("✓ ElevenLabs: Generated audio")

    # Test Veo
    video = await veo_service.generate_video(test_prompt)
    print("✓ Veo: Generated video")
```

---

## Additional Resources

- **YouTube Data API**: https://developers.google.com/youtube/v3
- **Gemini API**: https://ai.google.dev/
- **Vertex AI**: https://cloud.google.com/vertex-ai
- **ElevenLabs Docs**: https://elevenlabs.io/docs
- **Remotion Docs**: https://www.remotion.dev/docs
- **Veo Access**: Contact Google Cloud sales or check for updates
