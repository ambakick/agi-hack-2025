"""ElevenLabs service for text-to-speech conversion."""
import logging
from typing import Optional, List
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from app.models.schemas import ScriptResponse, ScriptSegment, PodcastFormat

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for converting text to speech using ElevenLabs."""
    
    # Default voice IDs (popular ElevenLabs voices)
    DEFAULT_VOICE_HOST1 = "21m00Tcm4TlvDq8ikWAM"  # Rachel - warm female voice
    DEFAULT_VOICE_HOST2 = "29vD33N1CtxCmqQRPOHJ"  # Drew - friendly male voice
    
    def __init__(self, api_key: str):
        """Initialize ElevenLabs service."""
        self.client = ElevenLabs(api_key=api_key)
        self.api_key = api_key
    
    async def generate_audio(
        self,
        script: ScriptResponse,
        voice_id_host1: Optional[str] = None,
        voice_id_host2: Optional[str] = None,
        output_format: str = "mp3_44100_128"
    ) -> bytes:
        """
        Generate audio from script using text-to-speech.
        
        Args:
            script: Complete podcast script
            voice_id_host1: Voice ID for HOST_1 (or single host)
            voice_id_host2: Voice ID for HOST_2 (multi-host only)
            output_format: Audio output format
            
        Returns:
            Audio data as bytes
        """
        try:
            # Use default voices if not specified
            voice1 = voice_id_host1 or self.DEFAULT_VOICE_HOST1
            voice2 = voice_id_host2 or self.DEFAULT_VOICE_HOST2
            
            if script.format == PodcastFormat.SINGLE_HOST:
                # Single host - generate entire script at once
                logger.info("Generating single-host audio...")
                audio_data = self._generate_speech(
                    text=script.full_script,
                    voice_id=voice1,
                    output_format=output_format
                )
                return audio_data
            
            else:
                # Multi-host - generate each segment with appropriate voice
                logger.info(f"Generating multi-host audio with {len(script.segments)} segments...")
                
                audio_segments = []
                for i, segment in enumerate(script.segments):
                    voice_id = voice1 if segment.speaker == "HOST_1" else voice2
                    
                    logger.debug(f"Generating segment {i+1}/{len(script.segments)} ({segment.speaker})")
                    
                    audio_data = self._generate_speech(
                        text=segment.text,
                        voice_id=voice_id,
                        output_format=output_format
                    )
                    audio_segments.append(audio_data)
                
                # Concatenate all audio segments
                return b''.join(audio_segments)
        
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise
    
    def _generate_speech(
        self,
        text: str,
        voice_id: str,
        output_format: str = "mp3_44100_128"
    ) -> bytes:
        """
        Generate speech for a single text segment.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            output_format: Audio format
            
        Returns:
            Audio data as bytes
        """
        try:
            # Generate audio using ElevenLabs API v1.0+
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_turbo_v2_5",
                output_format=output_format,
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.5,
                    use_speaker_boost=True
                )
            )
            
            # Collect all audio chunks
            audio_chunks = []
            for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)
            
            return b''.join(audio_chunks)
            
        except Exception as e:
            logger.error(f"Error in TTS generation: {str(e)}")
            raise
    
    async def get_available_voices(self) -> List[dict]:
        """
        Get list of available voices from ElevenLabs.
        
        Returns:
            List of voice information dictionaries
        """
        try:
            response = self.client.voices.get_all()
            
            voice_list = []
            for voice in response.voices:
                voice_list.append({
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', None),
                    "description": getattr(voice, 'description', None),
                })
            
            logger.info(f"Retrieved {len(voice_list)} available voices")
            return voice_list
            
        except Exception as e:
            logger.error(f"Error fetching voices: {str(e)}")
            raise
