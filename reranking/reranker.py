from typing import Any
import math


class SimpleReranker:
    """Rerank by semantic similarity approximation using embedding dot product."""

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = float(sum(x * y for x, y in zip(a, b)))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def rerank(self, query_embedding: list[float], candidates: list[dict[str, Any]], candidate_embeddings: list[list[float]], top_k: int) -> list[dict[str, Any]]:
        scored = []
        for item, emb in zip(candidates, candidate_embeddings):
            semantic_score = self._cosine(query_embedding, emb)
            new_item = dict(item)
            new_item["rerank_score"] = semantic_score
            scored.append(new_item)

        return sorted(scored, key=lambda x: x["rerank_score"], reverse=True)[:top_k]
