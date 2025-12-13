"""TTS endpoint for converting scripts to audio."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.models.schemas import TTSRequest
from app.services.elevenlabs import ElevenLabsService
from app.api.v1.deps import get_elevenlabs_service

router = APIRouter()


@router.post("/tts")
async def convert_to_speech(
    request: TTSRequest,
    elevenlabs_service: ElevenLabsService = Depends(get_elevenlabs_service)
):
    """
    Convert podcast script to audio using text-to-speech.
    
    Args:
        request: TTS request with script and voice preferences
        elevenlabs_service: ElevenLabs service instance
        
    Returns:
        Audio file as streaming response
    """
    try:
        audio_data = await elevenlabs_service.generate_audio(
            script=request.script,
            voice_id_host1=request.voice_id_host1,
            voice_id_host2=request.voice_id_host2
        )
        
        # Return audio as streaming response
        audio_stream = BytesIO(audio_data)
        
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=podcast.mp3"
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error converting to speech: {str(e)}"
        )


@router.get("/voices")
async def get_available_voices(
    elevenlabs_service: ElevenLabsService = Depends(get_elevenlabs_service)
):
    """
    Get list of available ElevenLabs voices.
    
    Returns:
        List of available voices
    """
    try:
        voices = await elevenlabs_service.get_available_voices()
        return {"voices": voices}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching voices: {str(e)}"
        )

