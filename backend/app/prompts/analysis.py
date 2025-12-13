"""Prompt template for content analysis."""

ANALYSIS_PROMPT = """You are an expert podcast researcher and content analyst. Your task is to analyze podcast transcripts and extract key themes, discussion points, and interesting anecdotes.

**Topic**: {{ topic }}

**Transcripts to Analyze**:
{% for transcript in transcripts %}
---
Video Title: {{ transcript.title }}
Video ID: {{ transcript.video_id }}

Transcript:
{{ transcript.transcript[:5000] }}
{% if transcript.transcript|length > 5000 %}... (truncated){% endif %}

---
{% endfor %}

**Your Task**:
1. Identify 5-8 major themes or topics discussed across these podcasts
2. For each theme, provide:
   - A clear theme name
   - A 2-3 sentence description
   - Which videos discuss this theme (by video ID)
3. Extract 3-5 interesting anecdotes, stories, or unique insights mentioned
4. Provide a 1-paragraph summary of what these podcasts collectively cover

**Output Format** (strict JSON):
```json
{
  "themes": [
    {
      "theme": "Theme Name",
      "description": "Description here",
      "sources": ["video_id_1", "video_id_2"]
    }
  ],
  "key_anecdotes": [
    "Anecdote or interesting fact here"
  ],
  "summary": "Overall summary paragraph here"
}
```

Return ONLY the JSON object, no additional text.
"""

