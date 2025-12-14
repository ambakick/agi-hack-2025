"""Graphon service for building knowledge graphs from uploaded files and querying them."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from app.core.config import settings
from app.models.schemas import (
    GraphContext,
    GraphContextRequest,
    GraphEntity,
    GraphRelation,
    GraphCitation,
    Source,
    SourceType,
)

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    """
    Extract JSON object from a possibly-markdown wrapped string.
    """
    s = (text or "").strip()
    if "```json" in s:
        start = s.find("```json") + len("```json")
        end = s.find("```", start)
        s = s[start:end].strip() if end != -1 else s[start:].strip()
    elif "```" in s:
        start = s.find("```") + len("```")
        end = s.find("```", start)
        s = s[start:end].strip() if end != -1 else s[start:].strip()
    return json.loads(s)


class GraphonService:
    """
    Thin wrapper around GraphonClient (per https://hackathon.graphon.ai/docs).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.graphon_api_key

    async def build_context(self, topic: str, sources: List[Source]) -> GraphContext:
        if not self.api_key:
            raise ValueError("GRAPHON_API_KEY is not set")

        # Import here so the backend can boot even if graphon-client isn't installed yet.
        from graphon_client import GraphonClient  # type: ignore

        client = GraphonClient(api_key=self.api_key)

        # Graphon docs: supports video/document/image; we skip audio for now.
        file_sources = [
            s
            for s in sources
            if s.type in (SourceType.PDF, SourceType.VIDEO, SourceType.IMAGE)
            and s.file_path
        ]

        if not file_sources:
            return GraphContext(summary="", entities=[], relations=[])

        # Resolve to absolute local paths
        file_paths: List[str] = []
        for s in file_sources:
            p = Path(s.file_path)
            if not p.is_absolute():
                p = (Path.cwd() / p).resolve()
            if not p.exists():
                logger.warning(f"Graphon source file missing on disk: {p}")
                continue
            file_paths.append(str(p))

        if not file_paths:
            return GraphContext(summary="", entities=[], relations=[])

        group_name = f"podcast-{topic[:40]}".strip() or "podcast-group"

        # One-shot: upload/process and create group
        group_id = await client.upload_process_and_create_group(
            file_paths=file_paths,
            group_name=group_name,
        )

        query = (
            "Return STRICT JSON with keys: summary, entities, relations. "
            "entities: [{name,type,description,citations:[{source_id,source_name,location,quote}]}]. "
            "relations: [{source,target,type,description,citations:[{source_id,source_name,location,quote}]}]. "
            f"Focus on the topic: {topic}. "
            "Use the uploaded sources as evidence; keep it concise."
        )

        response = await client.query_group(
            group_id=group_id,
            query=query,
            return_source_data=True,
        )

        # Graphon returns `answer` + `sources`. We ask for JSON in answer.
        raw_answer = getattr(response, "answer", "") or ""
        try:
            parsed = _extract_json(raw_answer)
        except Exception:
            # Fallback: just return the natural language answer as summary
            logger.warning("Graphon response was not JSON; returning as summary")
            return GraphContext(summary=raw_answer, entities=[], relations=[])

        def _parse_citations(items) -> List[GraphCitation]:
            citations: List[GraphCitation] = []
            for c in items or []:
                try:
                    citations.append(GraphCitation(**c))
                except Exception:
                    continue
            return citations

        entities: List[GraphEntity] = []
        for e in parsed.get("entities", []) or []:
            entities.append(
                GraphEntity(
                    name=e.get("name", ""),
                    type=e.get("type", "Other"),
                    description=e.get("description", ""),
                    citations=_parse_citations(e.get("citations")),
                )
            )

        relations: List[GraphRelation] = []
        for r in parsed.get("relations", []) or []:
            relations.append(
                GraphRelation(
                    source=r.get("source", ""),
                    target=r.get("target", ""),
                    type=r.get("type", ""),
                    description=r.get("description"),
                    citations=_parse_citations(r.get("citations")),
                )
            )

        return GraphContext(
            summary=parsed.get("summary", "") or "",
            entities=entities,
            relations=relations,
        )


