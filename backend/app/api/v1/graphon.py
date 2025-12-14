"""Graphon (knowledge graph) endpoints."""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import GraphContextRequest, GraphContext
from app.services.graphon_service import GraphonService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/graphon/context", response_model=GraphContext)
async def build_graph_context(
    request: GraphContextRequest,
) -> GraphContext:
    """
    Build Graphon context (entities/relations) from additional uploaded sources.

    This is intended to complement YouTube transcripts when generating an outline.
    """
    try:
        service = GraphonService()
        context = await service.build_context(topic=request.topic, sources=request.sources)
        return context
    except Exception as e:
        logger.error(f"Error building graph context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error building graph context: {str(e)}")


