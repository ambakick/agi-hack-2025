"""Prompt template for outline generation."""

OUTLINE_PROMPT = """You are an expert podcast producer. Create a structured outline for a {{ target_duration_minutes }}-minute podcast episode on the topic "{{ topic }}".

**Podcast Format**: {{ format }}
{% if format == "multi_host" %}
(This will be a conversational podcast with two hosts)
{% else %}
(This will be narrated by a single host)
{% endif %}

**Content Analysis**:

**Key Themes**:
{% for theme in themes %}
- {{ theme.theme }}: {{ theme.description }}
{% endfor %}

**Key Anecdotes**:
{% for anecdote in key_anecdotes %}
- {{ anecdote }}
{% endfor %}

**Summary**: {{ summary }}

**Your Task**:
Create a detailed outline with 4-6 sections. Each section should:
1. Have a clear, engaging title
2. Include a description of what will be covered
3. Specify estimated duration in minutes
4. List 2-4 key points to discuss

The outline should:
- Start with an engaging introduction (1-2 minutes)
- Flow logically through the main topics
- Include interesting stories/anecdotes at appropriate points
{% if format == "multi_host" %}
- Create opportunities for conversational back-and-forth between hosts
{% endif %}
- End with a memorable conclusion (1-2 minutes)

**Output Format** (strict JSON):
```json
{
  "sections": [
    {
      "id": "section_1",
      "title": "Section Title",
      "description": "What this section covers",
      "duration_minutes": 2.5,
      "key_points": [
        "First point to discuss",
        "Second point to discuss"
      ]
    }
  ],
  "total_duration_minutes": {{ target_duration_minutes }},
  "format": "{{ format }}"
}
```

Return ONLY the JSON object, no additional text.
"""

