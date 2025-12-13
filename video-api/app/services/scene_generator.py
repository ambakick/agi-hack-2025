"""Service for generating 8-second scene descriptions for Veo."""

import logging
import json
from typing import List
import google.generativeai as genai
from app.models.schemas import Snippet, SceneDescription, SceneGenerationResponse

logger = logging.getLogger(__name__)


class SceneGenerator:
    """Service for generating scene descriptions from snippets."""
    
    def __init__(self, api_key: str):
        """Initialize scene generator with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.scene_duration = 8.0  # Veo max duration
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Extract and parse JSON from model response."""
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
    
    async def generate_scenes(
        self,
        snippets: List[Snippet],
        scene_duration: float = 8.0
    ) -> SceneGenerationResponse:
        """
        Generate 8-second scene descriptions from snippets.
        
        Args:
            snippets: List of extracted snippets
            scene_duration: Duration for each scene (default 8 seconds)
            
        Returns:
            SceneGenerationResponse with scene descriptions
        """
        try:
            snippets_text = "\n\n".join([
                f"Snippet {i+1}:\n{snippet.text}\nContext: {snippet.context or 'N/A'}"
                for i, snippet in enumerate(snippets)
            ])
            
            prompt = f"""
You are an expert AI Cinematographer and Visual Director. Your goal is to translate podcast transcript snippets into detailed, photorealistic video generation prompts optimized for Google Veo 3.1.

TRANSCRIPT SNIPPETS:
{snippets_text}

**YOUR OBJECTIVE:**
Convert each snippet into a detailed visual scene description for video generation. Each scene will be exactly {scene_duration} seconds long and will be SILENT (no audio). The audio will be added separately later.

**CRITICAL CONSTRAINTS:**
1. Each scene must be exactly {scene_duration} seconds
2. NO audio, vocals, speech, or sound effects in the video description
3. NO visible people speaking, singing, or facing the camera
4. NO lip movement of any kind
5. NO on-screen text, subtitles, or captions
6. NO podcast studios, microphones, or interview setups
7. Visualize the STORY being told, not people talking

**PROMPT FORMAT:**
Each visual prompt must start with:
"Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio."

Then add:
- [Camera Movement/Angle] + [Subject Description] + [Action/Movement] + [Environment/Lighting] + [Film Style/Aesthetics]

**GUIDELINES:**
- Use specific camera terms: "Low-angle dolly shot," "Aerial drone view," "Close-up macro shot"
- Describe lighting: "Golden hour sunlight," "Neon cyberpunk lighting," "Soft cinematic diffusion"
- Specify style: "35mm film grain," "4k sharp digital," "Cinematic documentary style"
- Translate abstract concepts into visual metaphors
- Make scenes visually engaging and cinematic

**OUTPUT FORMAT (JSON):**
{{
  "scenes": [
    {{
      "scene_number": 1,
      "transcript_text": "original snippet text",
      "visual_prompt": "Cinematic lighting, photorealistic 4k, vertical 9:16 aspect ratio. [detailed visual description]",
      "duration": {scene_duration},
      "start_time": 0.0
    }}
  ]
}}

Return ONLY valid JSON, no additional text.
"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=6000,
                )
            )
            
            result = self._parse_json_response(response.text)
            
            scenes = [
                SceneDescription(**scene) for scene in result.get('scenes', [])
            ]
            
            # Ensure all scenes have correct duration
            for scene in scenes:
                scene.duration = scene_duration
            
            total_duration = len(scenes) * scene_duration
            
            logger.info(f"Generated {len(scenes)} scene descriptions")
            return SceneGenerationResponse(
                scenes=scenes,
                total_duration=total_duration
            )
            
        except Exception as e:
            logger.error(f"Error generating scenes: {str(e)}")
            raise

