"""Google Cloud Text-to-Speech service for text-to-speech conversion."""
import logging
from typing import Optional, List
from google.cloud import texttospeech
from google.api_core import client_options as client_options_lib
from app.models.schemas import ScriptResponse, ScriptSegment, PodcastFormat

logger = logging.getLogger(__name__)


class GoogleTTSService:
    """Service for converting text to speech using Google Cloud Text-to-Speech."""
    
    # Default voice names (Google Neural2 voices)
    DEFAULT_VOICE_HOST1 = "en-US-Neural2-F"  # Female - warm and professional
    DEFAULT_VOICE_HOST2 = "en-US-Neural2-J"  # Male - conversational and friendly
    
    def __init__(self, api_key: str):
        """Initialize Google TTS service."""
        # Initialize client with API key
        client_opts = client_options_lib.ClientOptions(api_key=api_key)
        self.client = texttospeech.TextToSpeechClient(client_options=client_opts)
        self.api_key = api_key
    
    async def generate_audio(
        self,
        script: ScriptResponse,
        voice_id_host1: Optional[str] = None,
        voice_id_host2: Optional[str] = None,
        output_format: str = "mp3"
    ) -> bytes:
        """
        Generate audio from script using text-to-speech.
        
        Args:
            script: Complete podcast script
            voice_id_host1: Voice name for HOST_1 (or single host)
            voice_id_host2: Voice name for HOST_2 (multi-host only)
            output_format: Audio output format (mp3, linear16, ogg_opus)
            
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
                    voice_name=voice1,
                    output_format=output_format
                )
                return audio_data
            
            else:
                # Multi-host - generate each segment with appropriate voice
                logger.info(f"Generating multi-host audio with {len(script.segments)} segments...")
                
                audio_segments = []
                for i, segment in enumerate(script.segments):
                    voice_name = voice1 if segment.speaker == "HOST_1" else voice2
                    
                    logger.debug(f"Generating segment {i+1}/{len(script.segments)} ({segment.speaker})")
                    
                    audio_data = self._generate_speech(
                        text=segment.text,
                        voice_name=voice_name,
                        output_format=output_format
                    )
                    audio_segments.append(audio_data)
                
                # Concatenate all audio segments
                return b''.join(audio_segments)
        
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise
    
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
    
    def _generate_speech(
        self,
        text: str,
        voice_name: str,
        output_format: str = "mp3"
    ) -> bytes:
        """
        Generate speech for a single text segment.
        Automatically splits long text into chunks if needed.
        
        Args:
            text: Text to convert to speech
            voice_name: Google TTS voice name (e.g., 'en-US-Neural2-F')
            output_format: Audio format (mp3, linear16, ogg_opus)
            
        Returns:
            Audio data as bytes
        """
        try:
            # Check if text needs to be split (5000 byte limit)
            text_chunks = self._split_text(text)
            
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
                    name=voice_name
                )
                
                # Select the audio encoding
                audio_encoding_map = {
                    "mp3": texttospeech.AudioEncoding.MP3,
                    "linear16": texttospeech.AudioEncoding.LINEAR16,
                    "ogg_opus": texttospeech.AudioEncoding.OGG_OPUS,
                }
                audio_encoding = audio_encoding_map.get(output_format, texttospeech.AudioEncoding.MP3)
                
                # Configure audio settings
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=audio_encoding,
                    speaking_rate=1.0,  # Normal speaking rate
                    pitch=0.0,  # Neutral pitch
                    sample_rate_hertz=24000 if output_format == "mp3" else None
                )
                
                # Perform the text-to-speech request
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                audio_segments.append(response.audio_content)
            
            # Concatenate all audio segments
            return b''.join(audio_segments)
            
        except Exception as e:
            logger.error(f"Error in TTS generation: {str(e)}")
            raise
    
    async def get_available_voices(self) -> List[dict]:
        """
        Get list of available voices from Google Cloud TTS.
        
        Returns:
            List of voice information dictionaries
        """
        try:
            # Fetch all available voices
            response = self.client.list_voices(language_code="en-US")
            
            voice_list = []
            for voice in response.voices:
                # Filter for Neural2 voices (best quality)
                if "Neural2" in voice.name:
                    voice_list.append({
                        "voice_id": voice.name,
                        "name": voice.name,
                        "language_codes": list(voice.language_codes),
                        "ssml_gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                        "natural_sample_rate_hertz": voice.natural_sample_rate_hertz,
                    })
            
            logger.info(f"Retrieved {len(voice_list)} Neural2 voices")
            return voice_list
            
        except Exception as e:
            logger.error(f"Error fetching voices: {str(e)}")
            raise
