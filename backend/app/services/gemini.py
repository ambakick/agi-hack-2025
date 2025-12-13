"""Gemini service for AI-powered content analysis and generation."""
import logging
import json
from typing import List, Optional
import google.generativeai as genai
from jinja2 import Template
from app.models.schemas import (
    VideoTranscript,
    AnalysisResponse,
    ThemePoint,
    OutlineResponse,
    OutlineSection,
    ScriptResponse,
    ScriptSegment,
    PodcastFormat,
)
from app.prompts.analysis import ANALYSIS_PROMPT
from app.prompts.outline import OUTLINE_PROMPT
from app.prompts.script import SCRIPT_SINGLE_HOST_PROMPT, SCRIPT_MULTI_HOST_PROMPT

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""
    
    def __init__(self, api_key: str):
        """Initialize Gemini service."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info(f"Initialized Gemini with model: gemini-2.0-flash-exp")
    
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
    
    async def analyze_content(
        self,
        transcripts: List[VideoTranscript],
        topic: str
    ) -> AnalysisResponse:
        """
        Analyze podcast transcripts to extract themes and key points.
        
        Args:
            transcripts: List of video transcripts
            topic: The main topic
            
        Returns:
            AnalysisResponse with themes and insights
        """
        try:
            # Render prompt template
            template = Template(ANALYSIS_PROMPT)
            prompt = template.render(
                topic=topic,
                transcripts=[t.dict() for t in transcripts]
            )
            
            # Generate response
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            # Parse into structured response
            themes = [
                ThemePoint(**theme) for theme in result.get('themes', [])
            ]
            
            analysis = AnalysisResponse(
                themes=themes,
                key_anecdotes=result.get('key_anecdotes', []),
                summary=result.get('summary', '')
            )
            
            logger.info(f"Content analysis completed: {len(themes)} themes identified")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            raise
    
    async def generate_outline(
        self,
        analysis: AnalysisResponse,
        topic: str,
        format: PodcastFormat,
        target_duration_minutes: int = 15
    ) -> OutlineResponse:
        """
        Generate podcast episode outline.
        
        Args:
            analysis: Content analysis results
            topic: Episode topic
            format: Single or multi-host format
            target_duration_minutes: Target episode duration
            
        Returns:
            OutlineResponse with structured sections
        """
        try:
            # Render prompt template
            template = Template(OUTLINE_PROMPT)
            prompt = template.render(
                topic=topic,
                format=format.value,
                target_duration_minutes=target_duration_minutes,
                themes=[t.dict() for t in analysis.themes],
                key_anecdotes=analysis.key_anecdotes,
                summary=analysis.summary
            )
            
            # Generate response
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            # Parse into structured response
            sections = [
                OutlineSection(**section) for section in result.get('sections', [])
            ]
            
            outline = OutlineResponse(
                sections=sections,
                total_duration_minutes=result.get('total_duration_minutes', target_duration_minutes),
                format=PodcastFormat(result.get('format', format.value))
            )
            
            logger.info(f"Outline generated: {len(sections)} sections")
            return outline
            
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            raise
    
    async def generate_script(
        self,
        outline: OutlineResponse,
        topic: str,
        format: PodcastFormat,
        style_notes: Optional[str] = None
    ) -> ScriptResponse:
        """
        Generate full podcast script from outline.
        
        Args:
            outline: Episode outline
            topic: Episode topic
            format: Single or multi-host format
            style_notes: Optional style guidelines
            
        Returns:
            ScriptResponse with full script and segments
        """
        try:
            # Choose appropriate prompt template
            if format == PodcastFormat.MULTI_HOST:
                template = Template(SCRIPT_MULTI_HOST_PROMPT)
            else:
                template = Template(SCRIPT_SINGLE_HOST_PROMPT)
            
            # Render prompt
            prompt = template.render(
                topic=topic,
                sections=[s.dict() for s in outline.sections],
                style_notes=style_notes
            )
            
            # Generate response with higher token limit
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=8000,
                    temperature=0.9,
                )
            )
            result = self._parse_json_response(response.text)
            
            # Parse into structured response
            segments = [
                ScriptSegment(**segment) for segment in result.get('segments', [])
            ]
            
            script = ScriptResponse(
                segments=segments,
                format=PodcastFormat(result.get('format', format.value)),
                total_duration_seconds=result.get('total_duration_seconds', 900.0),
                full_script=result.get('full_script', '')
            )
            
            logger.info(f"Script generated: {len(segments)} segments, {script.total_duration_seconds}s")
            return script
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise

