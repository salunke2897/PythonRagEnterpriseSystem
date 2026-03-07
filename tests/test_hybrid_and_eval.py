from retrieval.hybrid_search import HybridSearch
from services.evaluation_service import EvaluationService


def test_hybrid_scoring_order() -> None:
    hybrid = HybridSearch(vector_weight=0.7, keyword_weight=0.3)
    vector_results = [
        {"chunk_id": "a", "text": "alpha", "metadata": {}, "vector_score": 0.9},
        {"chunk_id": "b", "text": "beta", "metadata": {}, "vector_score": 0.4},
    ]
    keyword_results = [
        {"chunk_id": "b", "text": "beta", "metadata": {}, "keyword_score": 1.0},
    ]
    combined = hybrid.combine(vector_results, keyword_results, top_k=2)
    assert combined[0]["chunk_id"] == "a"
    assert combined[1]["chunk_id"] == "b"


def test_evaluation_scores_in_range() -> None:
    evaluator = EvaluationService()
    scores = evaluator.evaluate(
        question="What is the policy?",
        answer="The policy states data retention is 30 days.",
        retrieved_chunks=[{"text": "Data retention policy is 30 days."}],
    )
    assert 0.0 <= scores["context_relevance"] <= 1.0
    assert 0.0 <= scores["answer_groundedness"] <= 1.0
    assert 0.0 <= scores["answer_completeness"] <= 1.0
