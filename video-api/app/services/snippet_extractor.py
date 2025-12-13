"""Service for extracting interesting snippets from transcripts."""

import logging
import json
from typing import List, Union
import google.generativeai as genai
from app.models.schemas import TranscriptInput, Snippet, SnippetExtractionResponse

logger = logging.getLogger(__name__)


class SnippetExtractor:
    """Service for extracting interesting snippets from transcripts."""
    
    def __init__(self, api_key: str):
        """Initialize snippet extractor with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def _parse_transcript_text(self, transcript_input: TranscriptInput) -> str:
        """Convert transcript input to plain text."""
        if isinstance(transcript_input.transcript, str):
            return transcript_input.transcript
        elif isinstance(transcript_input.transcript, list):
            # Join timestamped segments
            return " ".join([seg.text for seg in transcript_input.transcript])
        else:
            raise ValueError("Invalid transcript format")
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Extract and parse JSON from model response."""
        # Try to find JSON in code blocks first
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            json_str = response_text.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}\nResponse: {json_str[:500]}")
            raise ValueError(f"Invalid JSON response from model: {str(e)}")
    
    async def extract_snippets(
        self,
        transcript_input: TranscriptInput,
        max_snippets: int = 5
    ) -> SnippetExtractionResponse:
        """
        Extract interesting snippets from transcript.
        
        Args:
            transcript_input: Transcript input (plain text or timestamped)
            max_snippets: Maximum number of snippets to extract
            
        Returns:
            SnippetExtractionResponse with extracted snippets
        """
        try:
            transcript_text = self._parse_transcript_text(transcript_input)
            
            prompt = f"""
You are selecting interesting, engaging snippets from a podcast transcript for use in video generation.

SOURCE TRANSCRIPT:
\"\"\"{transcript_text}\"\"\"

TASK:
Extract {max_snippets} compelling, continuous snippets from the transcript that would make excellent visual scenes for video generation.

SELECTION CRITERIA:
1. Choose snippets that are visually interesting and action-oriented
2. Prioritize descriptive content that can be visualized
3. Select moments with emotional impact or key insights
4. Each snippet should be approximately 8 seconds of spoken content
5. Snippets should be continuous (no skipping around within a snippet)
6. Replace speaker names with generic labels (e.g., "Person 1", "Person 2")

OUTPUT FORMAT (JSON):
{{
  "snippets": [
    {{
      "text": "exact transcript text",
      "start_time": 0.0,
      "end_time": 8.0,
      "context": "brief context about this snippet",
      "reason": "why this snippet was selected"
    }}
  ]
}}

Return ONLY valid JSON, no additional text.
"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=4000,
                )
            )
            
            result = self._parse_json_response(response.text)
            
            snippets = [
                Snippet(**snippet) for snippet in result.get('snippets', [])
            ]
            
            logger.info(f"Extracted {len(snippets)} snippets from transcript")
            return SnippetExtractionResponse(
                snippets=snippets,
                total_snippets=len(snippets)
            )
            
        except Exception as e:
            logger.error(f"Error extracting snippets: {str(e)}")
            raise

