"""Prompt template for script generation."""

SCRIPT_SINGLE_HOST_PROMPT = """You are a professional podcast scriptwriter. Write a compelling, conversational podcast script based on the outline below.

**Topic**: {{ topic }}

**Outline**:
{% for section in sections %}
### {{ section.title }} ({{ section.duration_minutes }} minutes)
{{ section.description }}

Key Points:
{% for point in section.key_points %}
- {{ point }}
{% endfor %}

{% endfor %}

**Style Requirements**:
- Write in a warm, conversational tone as if speaking directly to the listener
- Use natural speech patterns (contractions, casual language)
- Include smooth transitions between sections
- Make complex topics accessible and engaging
- Add rhetorical questions to keep listeners engaged
- Use storytelling techniques when presenting information
{% if style_notes %}
- Additional style notes: {{ style_notes }}
{% endif %}

**Format**: Single narrator speaking throughout

**Output Format** (strict JSON):
```json
{
  "segments": [
    {
      "section_id": "section_1",
      "speaker": "HOST_1",
      "text": "Full script text for this segment...",
      "timestamp_seconds": 0.0
    }
  ],
  "format": "single_host",
  "total_duration_seconds": 900.0,
  "full_script": "Complete script as a single text..."
}
```

Write the complete script. Estimate speaking time at ~150 words per minute. Return ONLY the JSON object.
"""


SCRIPT_MULTI_HOST_PROMPT = """You are a professional podcast scriptwriter. Write a dynamic, conversational podcast script with TWO HOSTS based on the outline below.

**Topic**: {{ topic }}

**Outline**:
{% for section in sections %}
### {{ section.title }} ({{ section.duration_minutes }} minutes)
{{ section.description }}

Key Points:
{% for point in section.key_points %}
- {{ point }}
{% endfor %}

{% endfor %}

**Style Requirements**:
- Create natural dialogue between HOST_1 and HOST_2
- Each host should have a distinct personality:
  - HOST_1: Slightly more enthusiastic, asks clarifying questions
  - HOST_2: More analytical, provides deeper insights
- Include natural interruptions, agreements, and reactions
- Use "um", "you know", "actually" sparingly for authenticity
- Hosts should build on each other's points
- Include moments of humor and banter where appropriate
- Make the conversation feel spontaneous yet well-informed
{% if style_notes %}
- Additional style notes: {{ style_notes }}
{% endif %}

**Example Opening**:
HOST_1: "Hey everyone, welcome back! Today we're diving into {{ topic }}."
HOST_2: "Yeah, this is fascinating stuff. I've been looking forward to this one."
HOST_1: "Same here! So where should we start?"

**Output Format** (strict JSON):
```json
{
  "segments": [
    {
      "section_id": "section_1",
      "speaker": "HOST_1",
      "text": "What this host says...",
      "timestamp_seconds": 0.0
    },
    {
      "section_id": "section_1",
      "speaker": "HOST_2",
      "text": "Response from other host...",
      "timestamp_seconds": 5.5
    }
  ],
  "format": "multi_host",
  "total_duration_seconds": 900.0,
  "full_script": "Complete script as a single text with speaker labels..."
}
```

Write the complete dialogue. Estimate speaking time at ~150 words per minute. Alternate between speakers naturally. Return ONLY the JSON object.
"""

