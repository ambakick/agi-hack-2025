"""Transcripts endpoint for retrieving YouTube video transcripts."""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import TranscriptRequest, TranscriptResponse
from app.services.youtube import YouTubeService
from app.api.v1.deps import get_youtube_service

router = APIRouter()


@router.post("/transcripts", response_model=TranscriptResponse)
async def get_transcripts(
    request: TranscriptRequest,
    youtube_service: YouTubeService = Depends(get_youtube_service)
) -> TranscriptResponse:
    """
    Retrieve transcripts for selected YouTube videos.
    
    Args:
        request: Transcript request with video IDs
        youtube_service: YouTube service instance
        
    Returns:
        Transcripts for the requested videos
    """
    try:
        if not request.video_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one video ID is required"
            )
        
        transcripts = await youtube_service.get_transcripts_batch(
            video_ids=request.video_ids,
            languages=['en']
        )
        
        if not transcripts:
            raise HTTPException(
                status_code=404,
                detail="No transcripts found for the provided video IDs"
            )
        
        return TranscriptResponse(transcripts=transcripts)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving transcripts: {str(e)}"
        )

