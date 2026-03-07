from typing import Any


class HybridSearch:
    def __init__(self, vector_weight: float = 0.7, keyword_weight: float = 0.3) -> None:
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight

    def combine(self, vector_results: list[dict[str, Any]], keyword_results: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}

        for item in vector_results:
            cid = item["chunk_id"]
            merged[cid] = {
                "chunk_id": cid,
                "text": item["text"],
                "metadata": item["metadata"],
                "vector_score": float(item.get("vector_score", 0.0)),
                "keyword_score": 0.0,
            }

        for item in keyword_results:
            cid = item["chunk_id"]
            if cid not in merged:
                merged[cid] = {
                    "chunk_id": cid,
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "vector_score": 0.0,
                    "keyword_score": float(item.get("keyword_score", 0.0)),
                }
            else:
                merged[cid]["keyword_score"] = float(item.get("keyword_score", 0.0))

        scored = []
        for value in merged.values():
            final_score = (self.vector_weight * value["vector_score"]) + (self.keyword_weight * value["keyword_score"])
            value["final_score"] = final_score
            scored.append(value)

        return sorted(scored, key=lambda x: x["final_score"], reverse=True)[:top_k]
