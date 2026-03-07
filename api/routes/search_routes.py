import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_retrieval_service
from models.response_models import SearchResponse, SearchResult
from services.retrieval_service import RetrievalService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/search", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=1, max_length=2000),
    top_k: int = Query(default=10, ge=1, le=50),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> SearchResponse:
    try:
        results, _ = await retrieval_service.retrieve(q, top_k=top_k)
        mapped = [
            SearchResult(
                chunk_id=item["chunk_id"],
                document_id=item["metadata"].get("document_id", ""),
                text=item["text"],
                source_file=item["metadata"].get("source_file", ""),
                page_number=int(item["metadata"].get("page_number", 0)),
                vector_score=float(item.get("vector_score", 0.0)),
                keyword_score=float(item.get("keyword_score", 0.0)),
                final_score=float(item.get("final_score", 0.0)),
            )
            for item in results
        ]
        return SearchResponse(results=mapped)
    except Exception as exc:
        logger.exception("document_search_failed")
        raise HTTPException(status_code=500, detail="Search failed") from exc
