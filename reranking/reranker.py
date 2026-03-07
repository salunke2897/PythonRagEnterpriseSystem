from typing import Any


class SimpleReranker:
    """Rerank by semantic similarity approximation using embedding dot product."""

    @staticmethod
    def _dot(a: list[float], b: list[float]) -> float:
        return float(sum(x * y for x, y in zip(a, b)))

    def rerank(self, query_embedding: list[float], candidates: list[dict[str, Any]], candidate_embeddings: list[list[float]], top_k: int) -> list[dict[str, Any]]:
        scored = []
        for item, emb in zip(candidates, candidate_embeddings):
            semantic_score = self._dot(query_embedding, emb)
            new_item = dict(item)
            new_item["rerank_score"] = semantic_score
            scored.append(new_item)

        return sorted(scored, key=lambda x: x["rerank_score"], reverse=True)[:top_k]
