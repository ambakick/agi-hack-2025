"""Script endpoint for generating podcast scripts."""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ScriptRequest, ScriptResponse
from app.services.gemini import GeminiService
from app.api.v1.deps import get_gemini_service

router = APIRouter()


@router.post("/script", response_model=ScriptResponse)
async def generate_script(
    request: ScriptRequest,
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> ScriptResponse:
    """
    Generate a complete podcast script from outline.
    
    Args:
        request: Script request with outline and parameters
        gemini_service: Gemini service instance
        
    Returns:
        Generated script with segments
    """
    try:
        script = await gemini_service.generate_script(
            outline=request.outline,
            topic=request.topic,
            format=request.format,
            style_notes=request.style_notes
        )
        
        return script
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating script: {str(e)}"
        )

