"""Outline endpoint for generating podcast outlines."""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import OutlineRequest, OutlineResponse
from app.services.gemini import GeminiService
from app.api.v1.deps import get_gemini_service

router = APIRouter()


@router.post("/outline", response_model=OutlineResponse)
async def generate_outline(
    request: OutlineRequest,
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> OutlineResponse:
    """
    Generate a structured podcast episode outline.
    
    Args:
        request: Outline request with analysis and parameters
        gemini_service: Gemini service instance
        
    Returns:
        Generated outline with sections
    """
    try:
        outline = await gemini_service.generate_outline(
            analysis=request.analysis,
            topic=request.topic,
            format=request.format,
            target_duration_minutes=request.target_duration_minutes
        )
        
        return outline
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating outline: {str(e)}"
        )

