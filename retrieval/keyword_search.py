from typing import Any
import re

from rank_bm25 import BM25Okapi


class KeywordSearch:
    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9]+", text.lower())

    async def search(self, query: str, corpus_records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not corpus_records:
            return []

        tokenized_corpus = [self._tokenize(record["text"]) for record in corpus_records]
        bm25 = BM25Okapi(tokenized_corpus)
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores = bm25.get_scores(query_tokens)

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
