"""Background worker entrypoints for asynchronous ingestion pipelines.

This module is intentionally lightweight and can be used from Celery/RQ/Kafka consumers.
"""

import asyncio

from core.config import get_settings
from ingestion.embedding_pipeline import EmbeddingPipeline
from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from vectorstore.chroma_store import ChromaStore


async def ingest_document(file_path: str) -> tuple[str, int]:
    settings = get_settings()
    service = DocumentService(
        pipeline=EmbeddingPipeline(settings),
        embedding_service=EmbeddingService(settings),
        vector_store=ChromaStore(persist_dir=settings.chroma_persist_dir),
    )
    return await service.ingest_pdf(file_path)


def ingest_document_sync(file_path: str) -> tuple[str, int]:
    return asyncio.run(ingest_document(file_path))
