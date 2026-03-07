from fastapi import Request

from core.config import get_settings
from ingestion.embedding_pipeline import EmbeddingPipeline
from reranking.reranker import SimpleReranker
from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.evaluation_service import EvaluationService
from services.llm_service import LLMService
from services.memory_service import MemoryService
from services.rag_service import RAGService
from services.rerank_service import RerankService
from services.retrieval_service import RetrievalService
from vectorstore.chroma_store import ChromaStore


def _ensure_services(request: Request) -> None:
    if getattr(request.app.state, "service_container", None) is not None:
        return

    settings = get_settings()
    cache = request.app.state.cache
    metrics = request.app.state.metrics
    memory_store = request.app.state.memory_store
    vector_store = ChromaStore(persist_dir=settings.chroma_persist_dir)

    embedding_service = EmbeddingService(settings)
    llm_service = LLMService(settings)
    document_service = DocumentService(EmbeddingPipeline(settings), embedding_service, vector_store)
    retrieval_service = RetrievalService(embedding_service, vector_store, cache)
    rerank_service = RerankService(embedding_service, SimpleReranker())
    memory_service = MemoryService(memory_store)
    evaluation_service = EvaluationService()
    rag_service = RAGService(
        retrieval_service=retrieval_service,
        rerank_service=rerank_service,
        llm_service=llm_service,
        memory_service=memory_service,
        evaluation_service=evaluation_service,
        rerank_top_k=settings.rerank_top_k,
        cache=cache,
        metrics_collector=metrics,
    )

    request.app.state.service_container = {
        "document_service": document_service,
        "retrieval_service": retrieval_service,
        "rag_service": rag_service,
    }


def get_document_service(request: Request) -> DocumentService:
    _ensure_services(request)
    return request.app.state.service_container["document_service"]


def get_retrieval_service(request: Request) -> RetrievalService:
    _ensure_services(request)
    return request.app.state.service_container["retrieval_service"]


def get_rag_service(request: Request) -> RAGService:
    _ensure_services(request)
    return request.app.state.service_container["rag_service"]
