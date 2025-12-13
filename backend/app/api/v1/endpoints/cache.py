"""Cache management endpoints."""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.core.cache import cache

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns cache size, number of entries, etc.
    """
    try:
        stats = cache.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/search")
async def clear_search_cache() -> Dict[str, str]:
    """Clear all search result cache."""
    try:
        cache.clear_search_cache()
        return {"success": True, "message": "Search cache cleared"}
    except Exception as e:
        logger.error(f"Error clearing search cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/transcripts")
async def clear_transcript_cache() -> Dict[str, str]:
    """Clear all transcript cache."""
    try:
        cache.clear_transcript_cache()
        return {"success": True, "message": "Transcript cache cleared"}
    except Exception as e:
        logger.error(f"Error clearing transcript cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear/all")
async def clear_all_cache() -> Dict[str, str]:
    """Clear all cache data."""
    try:
        cache.clear_all()
        return {"success": True, "message": "All cache cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

