"""Service for generating audio using Google Cloud Text-to-Speech."""

import logging
from pathlib import Path
from typing import List, Optional
from google.cloud import texttospeech
from google.api_core import client_options as client_options_lib
from app.models.schemas import SceneDescription, AudioScene, AudioGenerationResponse
from app.core.config import settings
from app.utils.video_utils import ensure_directory, get_output_path

logger = logging.getLogger(__name__)


class AudioService:
    """Service for generating audio using Google Cloud Text-to-Speech."""
    
    # Default voice name (Google Neural2 voice)
    DEFAULT_VOICE_ID = "en-US-Neural2-F"  # Female - warm and professional
    
    def __init__(self, api_key: str):
        """Initialize audio service with Google TTS API key."""
        # Initialize client with API key
        client_opts = client_options_lib.ClientOptions(api_key=api_key)
        self.client = texttospeech.TextToSpeechClient(client_options=client_opts)
        self.api_key = api_key
        self.output_dir = settings.audio_output_dir
    
    def _split_text(self, text: str, max_bytes: int = 4500) -> List[str]:
        """
        Split text into chunks that are under the byte limit.
        
        Args:
            text: Text to split
            max_bytes: Maximum bytes per chunk (default 4500 to be safe under 5000 limit)
            
        Returns:
            List of text chunks
        """
        # If text is under limit, return as-is
        if len(text.encode('utf-8')) <= max_bytes:
            return [text]
        
        # Split by sentences
        sentences = text.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|')
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed limit
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            if len(test_chunk.encode('utf-8')) <= max_bytes:
                current_chunk = test_chunk
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
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
            voice_id: Google TTS voice name (uses default if not provided)
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
            
            # Check if text needs to be split (5000 byte limit)
            text_chunks = self._split_text(scene.transcript_text)
            
            if len(text_chunks) > 1:
                logger.info(f"Text split into {len(text_chunks)} chunks for TTS")
            
            audio_segments = []
            
            for i, chunk in enumerate(text_chunks):
                logger.debug(f"Generating TTS for chunk {i+1}/{len(text_chunks)}")
                
                # Set the text input to be synthesized
                synthesis_input = texttospeech.SynthesisInput(text=chunk)
                
                # Build the voice request
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name=voice_id
                )
                
                # Configure audio settings for high quality MP3
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0,
                    sample_rate_hertz=24000
                )
                
                # Perform the text-to-speech request
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                audio_segments.append(response.audio_content)
            
            # Concatenate all audio segments
            audio_data = b''.join(audio_segments)
            
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
            voice_id: Google TTS voice name (uses default if not provided)
            
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
