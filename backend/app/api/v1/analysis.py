"""Analysis endpoint for content analysis using Gemini."""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.services.gemini import GeminiService
from app.api.v1.deps import get_gemini_service

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(
    request: AnalysisRequest,
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> AnalysisResponse:
    """
    Analyze podcast transcripts to extract themes and key points.
    
    Args:
        request: Analysis request with transcripts and topic
        gemini_service: Gemini service instance
        
    Returns:
        Analysis results with themes and insights
    """
    try:
        if not request.transcripts:
            raise HTTPException(
                status_code=400,
                detail="At least one transcript is required"
            )
        
        analysis = await gemini_service.analyze_content(
            transcripts=request.transcripts,
            topic=request.topic
        )
        
        return analysis
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing content: {str(e)}"
        )

