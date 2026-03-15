from typing import Any
import re

from retrieval.hybrid_search import HybridSearch
from retrieval.keyword_search import KeywordSearch
from retrieval.vector_search import VectorSearch
from services.embedding_service import EmbeddingService
from vectorstore.vector_store_interface import VectorStoreInterface


class RetrievalService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreInterface,
        cache: Any,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.cache = cache
        self.vector_search = VectorSearch(vector_store)
        self.keyword_search = KeywordSearch()
        self.hybrid_search = HybridSearch(vector_weight=vector_weight, keyword_weight=keyword_weight)

    @staticmethod
    def _expand_query(query: str) -> str:
        base = query.lower()
        tokens = set(re.findall(r"[a-zA-Z0-9]+", base))
        expansion = set(tokens)

        semantic_aliases = {
            "subject": {"subjects", "paper", "papers", "course", "courses", "curriculum", "syllabus"},
            "learned": {"learnt", "studied", "taken", "completed"},
            "marksheet": {"grade", "grades", "result", "transcript", "semester"},
            "person": {"student", "candidate", "learner"},
        }

        for key, aliases in semantic_aliases.items():
            if key in tokens:
                expansion.update(aliases)

        if "subject" in tokens or "subjects" in tokens:
            expansion.update({"subject_code", "subject name"})

        return " ".join(sorted(expansion))

    async def retrieve(self, query: str, top_k: int) -> tuple[list[dict[str, Any]], list[float]]:
        query_embedding_cache_key = f"embedding:query:{query}"
        cached_embedding = await self.cache.get(query_embedding_cache_key)
        query_embedding = cached_embedding or await self.embedding_service.embed_text(query)
        if cached_embedding is None:
            await self.cache.set(query_embedding_cache_key, query_embedding, ttl=3600)

        retrieval_cache_key = f"retrieval:query:{query}:k:{top_k}"
        cached_results = await self.cache.get(retrieval_cache_key)
        if cached_results is not None:
            return cached_results, query_embedding

        vector_results = await self.vector_search.search(query_embedding=query_embedding, top_k=top_k)
        corpus = await self.vector_store.get_all_documents()
        expanded_query = self._expand_query(query)
        keyword_results = await self.keyword_search.search(query=expanded_query, corpus_records=corpus, top_k=max(top_k * 3, top_k))

        combined = self.hybrid_search.combine(vector_results, keyword_results, top_k=top_k)
        await self.cache.set(retrieval_cache_key, combined, ttl=300)
        return combined, query_embedding
