from typing import Any

from rank_bm25 import BM25Okapi


class KeywordSearch:
    async def search(self, query: str, corpus_records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not corpus_records:
            return []

        tokenized_corpus = [record["text"].lower().split() for record in corpus_records]
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(query.lower().split())

        paired = sorted(zip(corpus_records, scores), key=lambda x: x[1], reverse=True)[:top_k]
        max_score = max((score for _, score in paired), default=1.0) or 1.0
        return [
            {
                "chunk_id": record["chunk_id"],
                "text": record["text"],
                "metadata": record["metadata"],
                "keyword_score": float(score / max_score),
            }
            for record, score in paired
        ]
