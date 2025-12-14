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

## Google Cloud Text-to-Speech API

### Overview
High-quality text-to-speech service from Google Cloud, offering Neural2 voices with natural-sounding speech for podcast narration.

### Setup
1. Create a Google Cloud Project at https://console.cloud.google.com
2. Enable the Cloud Text-to-Speech API
3. Create an API key or service account credentials
4. Install the Python client library: `pip install google-cloud-texttospeech`

### Authentication

**Option 1: API Key (Recommended for Development)**
```python
from google.cloud import texttospeech
from google.api_core import client_options as client_options_lib

GOOGLE_TTS_API_KEY = "your_api_key"
client_opts = client_options_lib.ClientOptions(api_key=GOOGLE_TTS_API_KEY)
client = texttospeech.TextToSpeechClient(client_options=client_opts)
```

**Option 2: Service Account (Recommended for Production)**
```python
from google.cloud import texttospeech
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/service-account-key.json'
client = texttospeech.TextToSpeechClient()
```

### Key Operations

#### 1. List Available Voices
```python
# List all available voices
response = client.list_voices(language_code="en-US")

for voice in response.voices:
    # Filter for Neural2 voices (highest quality)
    if "Neural2" in voice.name:
        print(f"Name: {voice.name}")
        print(f"Gender: {texttospeech.SsmlVoiceGender(voice.ssml_gender).name}")
        print(f"Languages: {', '.join(voice.language_codes)}")
        print(f"Sample Rate: {voice.natural_sample_rate_hertz}Hz")
        print("---")
```

**Recommended Neural2 Voices for Podcasts**:
- **en-US-Neural2-F**: Female, warm and professional
- **en-US-Neural2-J**: Male, conversational and friendly
- **en-US-Neural2-C**: Female, confident and clear
- **en-US-Neural2-D**: Male, authoritative and deep
- **en-US-Neural2-A**: Male, versatile and natural

#### 2. Text-to-Speech Conversion
```python
def synthesize_speech(text: str, voice_name: str = "en-US-Neural2-F") -> bytes:
    """Generate speech from text."""
    
    # Set the text input
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    # Configure the voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name
    )
    
    # Configure audio output
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,  # 0.25 to 4.0
        pitch=0.0,  # -20.0 to 20.0
        sample_rate_hertz=24000
    )
    
    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    return response.audio_content

# Use it
audio_data = synthesize_speech("Welcome to our podcast on AI innovations!")

# Save to file
with open("output.mp3", "wb") as f:
    f.write(audio_data)
```

#### 3. Multi-Voice Podcast (Dialog)
```python
def generate_multi_host_audio(segments: List[dict]) -> bytes:
    """Generate audio with multiple voices for dialog-style podcasts."""
    
    audio_parts = []
    
    for segment in segments:
        text = segment['text']
        speaker = segment['speaker']  # 'HOST_1' or 'HOST_2'
        
        # Choose voice based on speaker
        voice_name = "en-US-Neural2-F" if speaker == "HOST_1" else "en-US-Neural2-J"
        
        audio_data = synthesize_speech(text, voice_name)
        audio_parts.append(audio_data)
    
    # Concatenate all audio segments
    return b''.join(audio_parts)

# Example usage
script_segments = [
    {"speaker": "HOST_1", "text": "Welcome to the show!"},
    {"speaker": "HOST_2", "text": "Thanks for having me!"},
    {"speaker": "HOST_1", "text": "Let's dive into today's topic..."}
]

full_audio = generate_multi_host_audio(script_segments)
```

### Audio Configuration Options

#### Speaking Rate
- `0.25`: Very slow (accessibility)
- `1.0`: Normal speed (default)
- `1.2-1.5`: Slightly faster (common for podcasts)
- `4.0`: Maximum speed

#### Pitch
- `-20.0`: Very low pitch
- `0.0`: Natural pitch (default)
- `20.0`: Very high pitch

#### Sample Rate
- `24000`: Standard quality (recommended for podcasts)
- `44100`: CD quality
- `48000`: Professional audio

### Character Limits & Quotas
- **Maximum text length per request**: 5,000 characters
- **Default quota**: 1 million characters/month (free tier)
- **Pricing**: ~$16 per 1 million characters (Neural2 voices)

**Strategy for long scripts**:
```python
def split_text(text: str, max_chars: int = 4500) -> List[str]:
    """Split text at sentence boundaries for TTS."""
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= max_chars:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

async def generate_long_audio(text: str, voice_name: str) -> bytes:
    """Generate audio for text longer than 5000 characters."""
    chunks = split_text(text)
    audio_segments = []
    
    for chunk in chunks:
        audio_data = synthesize_speech(chunk, voice_name)
        audio_segments.append(audio_data)
    
    return b''.join(audio_segments)
```

### Error Handling
```python
from google.api_core.exceptions import GoogleAPIError, InvalidArgument

try:
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    audio_data = response.audio_content
    
except InvalidArgument as e:
    # Invalid voice name, language code, or text too long
    print(f"Invalid request: {e}")
    
except GoogleAPIError as e:
    # API error (quota exceeded, authentication failed, etc.)
    print(f"Google API error: {e}")
    
except Exception as e:
    # Other errors
    print(f"Unexpected error: {e}")
```

### Rate Limiting & Best Practices
- **No strict rate limits** with proper API key setup
- **Concurrent requests**: Supported, use async for parallel processing
- **Caching**: Cache generated audio to avoid redundant API calls
- **Error retry**: Implement exponential backoff for transient errors

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def synthesize_with_retry(text: str, voice_name: str) -> bytes:
    """Synthesize speech with automatic retry on failures."""
    return synthesize_speech(text, voice_name)
```

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
- [ ] Enable Google Cloud Text-to-Speech API, get API key
- [ ] Request Veo access (Vertex AI)
- [ ] Install Remotion
- [ ] Set up environment variables

### Environment Variables
```bash
# .env file
YOUTUBE_API_KEY=your_youtube_key
GEMINI_API_KEY=your_gemini_key
GOOGLE_TTS_API_KEY=your_google_tts_key

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

    # Test Google TTS
    audio = await google_tts_service.generate_audio("Test", voice_name)
    print("✓ Google TTS: Generated audio")

    # Test Veo
    video = await veo_service.generate_video(test_prompt)
    print("✓ Veo: Generated video")
```

---

## Additional Resources

- **YouTube Data API**: https://developers.google.com/youtube/v3
- **Gemini API**: https://ai.google.dev/
- **Vertex AI**: https://cloud.google.com/vertex-ai
- **Google Cloud TTS Docs**: https://cloud.google.com/text-to-speech/docs
- **Remotion Docs**: https://www.remotion.dev/docs
- **Veo Access**: Contact Google Cloud sales or check for updates
