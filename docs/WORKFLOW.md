# Podcast Generation System Workflow

## Overview
This document describes the complete end-to-end workflow for generating AI-powered podcast episodes from a topic prompt. The system produces three main outputs: audio file, video file, and show notes with timestamps.

## System Architecture
The workflow is composed of 11 sequential modules, each responsible for a specific part of the process. The system leverages multiple AI services and APIs to transform a simple topic into a complete multimedia podcast episode.

## Tech Stack
- **Backend**: Python 3.11+ with FastAPI
- **LLM**: Google Gemini 3 (content analysis, script writing, show notes)
- **TTS**: ElevenLabs API (natural voice synthesis)
- **Video Generation**: Google Veo (Vertex AI) + Remotion
- **Data Source**: YouTube Data API v3 (English podcasts only)
- **Additional Tools**: Python libraries for API integration, async processing

---

## Workflow Steps

### 1. Topic Input & Podcast Discovery

**Purpose**: Find relevant existing podcast content to use as reference material.

**Process**:
- User enters a topic or title for the desired podcast episode
- System uses YouTube Data API v3 to search for existing podcast episodes related to that topic
- Search is limited to English-language results only
- API returns a list of relevant YouTube videos (podcast recordings)

**Input**: Topic string (e.g., "The future of artificial intelligence")

**Output**: List of YouTube videos with metadata (video ID, title, channel, duration, view count)

**Implementation Notes**:
- Use `youtube.search.list` endpoint
- Parameters: `relevanceLanguage='en'`, `type='video'`
- Consider filtering by view count or upload date for quality
- Implement pagination if needed for more results
- Handle API quota limits (10,000 units/day)

**FastAPI Endpoint**: `POST /api/v1/discovery/search`

---

### 2. Reference Selection

**Purpose**: Allow user to curate which podcast episodes will inform the new content.

**Process**:
- User is presented with the top search results (e.g., 10-20 podcasts)
- Display relevant metadata: title, channel, duration, thumbnail
- User selects 2-5 episodes as references (configurable)
- Selected videos move forward to transcription

**Input**: List of YouTube videos from Step 1

**Output**: Filtered list of selected YouTube video IDs

**Implementation Notes**:
- Frontend UI should show video thumbnails and descriptions
- Allow multi-select functionality
- Store selections in session or database
- Validate that selected videos have captions available

**FastAPI Endpoint**: `POST /api/v1/references/select`

---

### 3. Transcription Retrieval

**Purpose**: Extract the spoken content from reference podcasts.

**Process**:
- For each selected YouTube video, retrieve the transcript
- Primary method: YouTube's caption/subtitle data
- Use YouTube Data API to fetch caption tracks
- Download and parse the caption file (SRT or VTT format)
- Fallback: Use open-source transcription tools if captions unavailable

**Input**: List of YouTube video IDs

**Output**: Raw transcript text for each video (plain text format)

**Implementation Notes**:
- Use `youtube.captions.list` and `youtube.captions.download` endpoints
- Parse SRT/VTT format to extract clean text (remove timestamps)
- Handle videos without captions gracefully
- Consider using speech-to-text API as fallback (e.g., Google Speech-to-Text)
- Store transcripts with video ID reference

**FastAPI Endpoint**: `POST /api/v1/transcription/retrieve`

**Example Service**:
```python
class TranscriptionService:
    async def get_transcript(self, video_id: str) -> str:
        # Try YouTube captions first
        # Fallback to STT if needed
        pass
```

---

### 4. Content Analysis

**Purpose**: Extract key themes, discussion points, and interesting anecdotes from transcripts.

**Process**:
- Send all retrieved transcripts to Google Gemini 3
- Prompt Gemini to analyze and extract:
  - Main themes and topics discussed
  - Key arguments or perspectives
  - Interesting stories, anecdotes, or examples
  - Notable facts or statistics mentioned
- Gemini returns structured analysis of content

**Input**: List of transcripts (text)

**Output**: Structured analysis containing themes, key points, anecdotes

**Implementation Notes**:
- Use Gemini 3's long context window for multiple transcripts
- Craft detailed prompts with examples of desired output format
- Request JSON output for easier parsing
- Aggregate insights from multiple transcripts
- De-duplicate similar themes across videos

**Prompt Template**:
```
Analyze these podcast transcripts and extract:
1. Main themes (3-5 major topics)
2. Key discussion points for each theme
3. Interesting stories or anecdotes
4. Notable facts or statistics

Output as structured JSON.

Transcripts:
[Insert transcripts here]
```

**FastAPI Endpoint**: `POST /api/v1/analysis/analyze`

---

### 5. Outline Generation

**Purpose**: Create a structured plan for the new podcast episode.

**Process**:
- Using insights from content analysis, generate an episode outline
- Gemini 3 proposes a draft outline with:
  - Introduction
  - Main segments/topics (3-5 sections)
  - Key points to cover in each segment
  - Conclusion
- User can review and modify the outline (partial human input)
- Approved outline moves to script writing

**Input**: Analysis results from Step 4, original topic

**Output**: Structured outline (JSON or markdown format)

**Implementation Notes**:
- Allow for human-in-the-loop editing
- Store outline versions (draft vs. approved)
- Outline should include estimated time for each segment
- Consider narrative flow and transitions
- Option to regenerate outline with different focus

**Prompt Template**:
```
Create a podcast episode outline based on this analysis.

Topic: [Original topic]
Key themes: [From analysis]

Structure:
- Engaging introduction (30 seconds)
- 3-5 main segments (2-3 minutes each)
- Smooth transitions
- Compelling conclusion (30 seconds)

Total target length: 10-15 minutes
```

**FastAPI Endpoint**: `POST /api/v1/outline/generate`

---

### 6. Script Writing with Gemini 3

**Purpose**: Generate the full conversational script for the podcast.

**Process**:
- Send approved outline to Gemini 3 with detailed instructions
- Gemini writes a full podcast script with:
  - Natural conversational tone
  - Engaging introduction that hooks listeners
  - Smooth transitions between topics
  - Expanded content for each outline point
  - Optional banter or Q&A style dialogue
  - Compelling conclusion with key takeaways
- Script can be single narrator or multi-speaker format
- Output is a complete, production-ready script

**Input**: Approved outline, content analysis, style preferences

**Output**: Full podcast script (plain text or structured format)

**Implementation Notes**:
- Use Gemini 3's advanced reasoning for narrative planning
- Specify desired tone: casual, professional, educational, entertaining
- Request specific length (word count or time estimate)
- Include examples of desired style in prompt
- Support multi-speaker format (Host A, Host B)
- Generate speaker attribution if multi-speaker

**Prompt Template**:
```
Write a complete podcast script based on this outline.

Outline: [Insert outline]
Content: [Key points from analysis]

Requirements:
- Conversational, engaging tone
- Natural spoken language (not overly formal)
- Include transitions between topics
- Length: approximately 2000-2500 words (10-12 minutes spoken)
- Style: [single narrator / two-host conversation]

Format:
[INTRO]
...script content...

[SEGMENT 1: Title]
...script content...
```

**FastAPI Endpoint**: `POST /api/v1/script/generate`

---

### 7. Fact-Checking (Optional)

**Purpose**: Verify accuracy of factual claims in the script.

**Process**:
- Identify factual statements in the script (dates, statistics, claims)
- Use LLM or web search API to verify facts
- Flag any questionable or unverified claims
- Optional human review of flagged items
- Correct inaccuracies in the script

**Input**: Generated script

**Output**: Verified script with corrections

**Implementation Notes**:
- Semi-automated process suitable for hackathon scope
- Use Gemini with search grounding for fact verification
- Or integrate web search API (Google Search, Brave Search)
- Priority: verify specific numbers, dates, scientific claims
- Can be simplified or skipped for time constraints
- Log all fact-check results for transparency

**FastAPI Endpoint**: `POST /api/v1/script/fact-check` (optional)

---

### 8. Text-to-Speech Conversion

**Purpose**: Transform the written script into natural-sounding audio.

**Process**:
- Send finalized script to ElevenLabs API
- Select voice(s): single narrator or multiple voices for different speakers
- ElevenLabs generates high-quality, natural-sounding speech
- Receive audio file(s) in MP3 or WAV format
- Concatenate segments if script was split
- Final audio is production-ready podcast narration

**Input**: Final script (text), voice selection

**Output**: Audio file (MP3/WAV format)

**Implementation Notes**:
- ElevenLabs API endpoint: `/v1/text-to-speech/{voice_id}`
- Choose appropriate voice IDs (professional, warm, energetic)
- Consider character limits per API request
- Split long scripts into manageable chunks
- Maintain consistent voice across segments
- Support for multi-voice (different speakers)
- Adjust speech rate, pitch if needed
- Output format: MP3 at 44.1kHz recommended

**Example Configuration**:
```python
voice_settings = {
    "stability": 0.5,
    "similarity_boost": 0.75
}
```

**FastAPI Endpoint**: `POST /api/v1/audio/generate`

---

### 9. Video Generation

**Purpose**: Create compelling visuals to accompany the audio.

**Process**: Two-stage video generation using Veo and Remotion.

#### Stage A: Scene Segmentation & Veo Generation

1. **Scene Breakdown**:
   - Use Gemini to analyze the script and divide it into 5-6 visual scenes (~5 seconds each)
   - Generate specific text-to-video prompts for each scene
   - Ensure visual consistency and narrative flow

2. **Prompt Generation**:
   - Each prompt includes: "Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio"
   - Add specific scene description (e.g., "abstract visualization of neural networks with glowing nodes")
   - Maintain consistent visual style across scenes

3. **Veo API Calls**:
   - Send prompts to Google Veo (via Vertex AI or VideoFX)
   - Veo generates high-definition, cinematic video clips
   - Receive HD video files (9:16 vertical format)
   - Unlike stock footage, these are custom-generated to match script

**Example Veo Prompt**:
```
Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio.
A futuristic cityscape at dawn with autonomous vehicles flowing smoothly through streets.
Camera slowly pans across the scene. Professional commercial quality.
```

#### Stage B: Remotion Video Assembly

1. **Project Setup**:
   - Use Remotion to create programmatic video composition
   - Define React components for different scene types:
     - `<IntroScene>`: Title card with topic
     - `<TopicSlide>`: Text overlays with key points
     - `<VeoClip>`: Generated video segments
     - `<OutroScene>`: Conclusion card

2. **Audio Synchronization**:
   - Import audio track from ElevenLabs
   - Align visual scenes to audio timeline
   - Calculate timestamps for scene transitions
   - Ensure video duration matches audio length

3. **Visual Elements**:
   - Veo-generated video clips as primary visuals
   - Text overlays for key points or quotes
   - Subtle animations (fade in/out, transitions)
   - Optional: waveform visualization for audio
   - Consistent branding elements

4. **Rendering**:
   - Remotion renders final MP4 video
   - Output: 1080x1920 (9:16 vertical format)
   - Synced audio and video
   - Professional-quality result

**Input**: Script, audio file, Veo video clips

**Output**: Final MP4 video file (9:16 format)

**Implementation Notes**:
- Use Gemini for intelligent scene segmentation
- Batch Veo API calls for efficiency
- Handle Veo rate limits and quotas
- Remotion can run as subprocess or via API
- Consider using Remotion Lambda for cloud rendering
- Template-based approach for faster development
- Ensure proper timing synchronization

**FastAPI Endpoints**:
- `POST /api/v1/video/segment-scenes`
- `POST /api/v1/video/generate-veo`
- `POST /api/v1/video/compose-remotion`

---

### 10. Show Notes & Timestamps

**Purpose**: Generate written summary and timeline for the episode.

**Process**:
- Send script and timeline to Gemini 3
- Generate comprehensive show notes including:
  - Episode summary (2-3 paragraphs)
  - List of topics with timestamps
  - Key takeaways
  - Resource links (if applicable)
- Format as markdown for easy publishing

**Input**: Script, audio/video timeline (segment durations)

**Output**: Formatted show notes with timestamps

**Example Output**:
```markdown
# Episode: The Future of Artificial Intelligence

## Summary
In this episode, we explore the latest developments in AI technology,
from large language models to autonomous systems...

## Timeline
- 00:00 - Introduction
- 01:30 - The Rise of Large Language Models
- 05:20 - Real-world Applications of AI
- 08:45 - Ethical Considerations
- 12:10 - Future Predictions
- 14:30 - Conclusion

## Key Takeaways
- AI is transforming multiple industries...
- Ethical frameworks are essential...
```

**Implementation Notes**:
- Calculate timestamps from script segments and audio duration
- Use Gemini to summarize each segment concisely
- Format consistently (HH:MM:SS or MM:SS)
- Include episode metadata (title, date, duration)
- SEO-friendly descriptions
- Markdown format for easy publishing

**Prompt Template**:
```
Generate show notes for this podcast episode.

Script: [Insert script]
Timeline: [Segment durations]

Include:
1. Episode summary (2-3 paragraphs)
2. Timestamped list of topics
3. Key takeaways (3-5 bullet points)

Format: Markdown
```

**FastAPI Endpoint**: `POST /api/v1/shownotes/generate`

---

### 11. Final Assembly & Delivery

**Purpose**: Package all outputs and deliver to user.

**Process**:
- Collect all generated assets:
  - Audio file (MP3/WAV)
  - Video file (MP4)
  - Show notes (Markdown)
- Validate all files are complete
- Package for download or streaming
- Optional: Auto-upload to platforms (YouTube, podcast host)
- Present results to user via web interface

**Input**: Audio file, video file, show notes

**Output**: Complete podcast episode package

**Implementation Notes**:
- Store files in cloud storage (S3, GCS)
- Generate unique episode ID
- Create manifest/metadata file
- Provide download links
- Optional: YouTube auto-upload via API
  - Use YouTube Data API `videos.insert`
  - Set video to unlisted
  - Populate description with show notes
- In-app preview: audio/video player + text display

**FastAPI Endpoint**: `POST /api/v1/episode/finalize`

**Response Format**:
```json
{
  "episode_id": "ep_12345",
  "status": "completed",
  "audio_url": "https://...",
  "video_url": "https://...",
  "show_notes": "...",
  "youtube_url": "https://youtube.com/..." (if uploaded)
}
```

---

## Data Flow Summary

```
User Topic Input
    ↓
YouTube Search → Video List
    ↓
User Selection → Selected Videos
    ↓
Transcription → Raw Text
    ↓
Gemini Analysis → Themes & Key Points
    ↓
Gemini Outline → Structured Plan
    ↓
Gemini Script → Full Script
    ↓
Fact Check → Verified Script
    ↓
    ├→ ElevenLabs TTS → Audio File
    ├→ Veo + Remotion → Video File
    └→ Gemini Show Notes → Show Notes
        ↓
    Final Package → Delivery
```

---

## Key Constraints & Requirements

- **Language**: English only (YouTube search, content, TTS)
- **Source Material**: YouTube podcasts exclusively
- **Output Formats**:
  - Audio: MP3 or WAV
  - Video: MP4, 9:16 vertical format (1080x1920)
  - Show Notes: Markdown with timestamps
- **Quality**: Production-ready, natural-sounding, professional-looking
- **Automation**: Minimal human intervention (outline approval optional)

---

## Error Handling & Edge Cases

- YouTube videos without captions → Fallback transcription or skip
- API rate limits → Implement queuing and retries
- Gemini failures → Retry with modified prompts
- ElevenLabs character limits → Split script intelligently
- Veo generation failures → Fallback to stock footage or simpler visuals
- Long processing times → Implement async job queue, status updates

---

## Future Enhancements

- Multi-language support
- Custom voice cloning (ElevenLabs)
- More video sources beyond YouTube
- Advanced editing: background music, sound effects
- Interactive transcript in video
- SEO optimization for publishing
- Analytics dashboard
- Batch processing multiple episodes
