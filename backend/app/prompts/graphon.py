"""Prompt template for extracting Graphon (knowledge graph) context from sources."""

GRAPHON_PROMPT = """You are building a small knowledge graph to help generate a high-quality podcast outline about the topic "{{ topic }}".

You will be given one or more uploaded source files (PDFs, images, audio, or video). Extract:
- Key ENTITIES relevant to the topic (people, organizations, places, events, concepts).
- Key RELATIONSHIPS between entities (e.g., "founded", "accused_of", "located_in", "caused", "influenced").

Rules:
- Prefer factual, source-grounded entities/relations.
- For each entity/relation, include at least one citation with a short quote/snippet and an approximate location (page number if PDF, timestamp if audio/video when possible).
- If the source does not contain relevant info, return empty lists but still include a short summary.

Return STRICT JSON in this schema:
```json
{
  "summary": "1-3 sentences summarizing what the uploaded sources add beyond the YouTube transcript.",
  "entities": [
    {
      "name": "EntityName",
      "type": "Person|Org|Place|Event|Concept|Other",
      "description": "Short description",
      "citations": [
        { "source_id": "source-id", "source_name": "optional", "location": "p. 3", "quote": "short snippet" }
      ]
    }
  ],
  "relations": [
    {
      "source": "EntityA",
      "target": "EntityB",
      "type": "relation_type",
      "description": "Optional short description",
      "citations": [
        { "source_id": "source-id", "source_name": "optional", "location": "p. 3", "quote": "short snippet" }
      ]
    }
  ]
}
```

Return ONLY the JSON object, no additional text.
"""


