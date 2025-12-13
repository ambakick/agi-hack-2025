"""Discovery endpoint for YouTube podcast search."""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import DiscoveryRequest, DiscoveryResponse
from app.services.youtube import YouTubeService
from app.api.v1.deps import get_youtube_service

router = APIRouter()


@router.post("/discover", response_model=DiscoveryResponse)
async def discover_podcasts(
    request: DiscoveryRequest,
    youtube_service: YouTubeService = Depends(get_youtube_service)
) -> DiscoveryResponse:
    """
    Search YouTube for podcast episodes related to a topic.
    
    Args:
        request: Discovery request with topic and parameters
        youtube_service: YouTube service instance
        
    Returns:
        List of relevant podcast videos
    """
    try:
        videos = await youtube_service.search_podcasts(
            query=request.topic,
            max_results=request.max_results,
            language=request.language
        )
        
        return DiscoveryResponse(
            videos=videos,
            query=request.topic
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching for podcasts: {str(e)}"
        )

