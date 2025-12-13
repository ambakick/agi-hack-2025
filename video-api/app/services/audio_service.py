"""Service for generating audio using ElevenLabs."""

import logging
from pathlib import Path
from typing import List, Optional
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from app.models.schemas import SceneDescription, AudioScene, AudioGenerationResponse
from app.core.config import settings
from app.utils.video_utils import ensure_directory, get_output_path

logger = logging.getLogger(__name__)


class AudioService:
    """Service for generating audio using ElevenLabs."""
    
    # Default voice ID (Rachel - warm female voice)
    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
    
    def __init__(self, api_key: str):
        """Initialize audio service with ElevenLabs API key."""
        self.client = ElevenLabs(api_key=api_key)
        self.api_key = api_key
        self.output_dir = settings.audio_output_dir
    
    async def generate_audio(
        self,
        scene: SceneDescription,
        voice_id: Optional[str] = None,
        output_filename: str = None
    ) -> AudioScene:
        """
        Generate audio for a single scene.
        
        Args:
            scene: Scene description with transcript text
            voice_id: ElevenLabs voice ID (uses default if not provided)
            output_filename: Optional output filename
            
        Returns:
            AudioScene with file path and metadata
        """
        try:
            if voice_id is None:
                voice_id = self.DEFAULT_VOICE_ID
            
            if output_filename is None:
                output_filename = f"audio_scene_{scene.scene_number}.mp3"
            
            output_path = get_output_path(self.output_dir, output_filename)
            
            logger.info(f"Generating audio for scene {scene.scene_number}...")
            
            # Generate audio using ElevenLabs API
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=scene.transcript_text,
                model_id="eleven_turbo_v2_5",
                output_format="mp3_44100_128",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.5,
                    use_speaker_boost=True
                )
            )
            
            # Collect all audio chunks and save
            audio_chunks = []
            for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)
            
            audio_data = b''.join(audio_chunks)
            
            # Save to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Audio saved to {output_path}")
            
            # Create audio scene (duration will be approximate, actual duration
            # will be determined when we process the audio file)
            audio_scene = AudioScene(
                scene_number=scene.scene_number,
                file_path=str(output_file),
                duration=scene.duration,  # Expected duration
                transcript_text=scene.transcript_text
            )
            
            return audio_scene
            
        except Exception as e:
            logger.error(f"Error generating audio for scene {scene.scene_number}: {str(e)}")
            raise
    
    async def generate_audio_clips(
        self,
        scenes: List[SceneDescription],
        voice_id: Optional[str] = None
    ) -> AudioGenerationResponse:
        """
        Generate audio clips for all scenes.
        
        Args:
            scenes: List of scene descriptions
            voice_id: ElevenLabs voice ID (uses default if not provided)
            
        Returns:
            AudioGenerationResponse with all generated audio clips
        """
        try:
            if voice_id is None:
                voice_id = self.DEFAULT_VOICE_ID
            
            logger.info(f"Generating {len(scenes)} audio clips...")
            
            audio_scenes = []
            for scene in scenes:
                audio_scene = await self.generate_audio(scene, voice_id)
                audio_scenes.append(audio_scene)
            
            total_duration = sum(as_.duration for as_ in audio_scenes)
            
            logger.info(f"Generated {len(audio_scenes)} audio clips, total duration: {total_duration}s")
            return AudioGenerationResponse(
                audio_scenes=audio_scenes,
                total_duration=total_duration,
                voice_id=voice_id
            )
            
        except Exception as e:
            logger.error(f"Error generating audio clips: {str(e)}")
            raise

