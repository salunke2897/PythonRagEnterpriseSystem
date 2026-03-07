from typing import Any

from reranking.reranker import SimpleReranker
from services.embedding_service import EmbeddingService


class RerankService:
    def __init__(self, embedding_service: EmbeddingService, reranker: SimpleReranker) -> None:
        self.embedding_service = embedding_service
        self.reranker = reranker

    async def rerank(self, question_embedding: list[float], candidates: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        candidate_embeddings = await self.embedding_service.embed_batch([c["text"] for c in candidates]) if candidates else []
        return self.reranker.rerank(question_embedding, candidates, candidate_embeddings, top_k=top_k)
