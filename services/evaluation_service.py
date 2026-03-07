from typing import Any


class EvaluationService:
    def score_context_relevance(self, question: str, contexts: list[str]) -> float:
        if not contexts:
            return 0.0
        q_terms = set(question.lower().split())
        overlaps = [len(q_terms & set(ctx.lower().split())) / max(len(q_terms), 1) for ctx in contexts]
        return float(sum(overlaps) / len(overlaps))

    def score_groundedness(self, answer: str, contexts: list[str]) -> float:
        if not answer or not contexts:
            return 0.0
        context_text = " ".join(contexts).lower()
        answer_terms = [term for term in answer.lower().split() if len(term) > 3]
        if not answer_terms:
            return 0.0
        grounded = sum(1 for term in answer_terms if term in context_text)
        return grounded / len(answer_terms)

    def score_completeness(self, answer: str) -> float:
        token_count = len(answer.split())
        return min(1.0, token_count / 80)

    def evaluate(self, question: str, answer: str, retrieved_chunks: list[dict[str, Any]]) -> dict[str, float]:
        contexts = [item["text"] for item in retrieved_chunks]
        return {
            "context_relevance": self.score_context_relevance(question, contexts),
            "answer_groundedness": self.score_groundedness(answer, contexts),
            "answer_completeness": self.score_completeness(answer),
        }
