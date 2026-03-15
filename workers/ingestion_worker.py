"""Background worker entrypoints for asynchronous ingestion pipelines.

This module is intentionally lightweight and can be used from Celery/RQ/Kafka consumers.
"""

import asyncio

from core.config import get_settings
from ingestion.ingestion_service import process_document
from services.embedding_service import EmbeddingService
from vectorstore.chroma_store import ChromaStore


async def ingest_document(file_path: str) -> tuple[str, int]:
    settings = get_settings()
    document_id, chunk_records, _ = await process_document(file_path=file_path, settings=settings)
    if not chunk_records:
        return document_id, 0

    embedding_service = EmbeddingService(settings)
    vector_store = ChromaStore(persist_dir=settings.chroma_persist_dir)

    texts = [record["text"] for record in chunk_records]
    embeddings = await embedding_service.embed_batch(texts)
    await vector_store.upsert(
        ids=[record["id"] for record in chunk_records],
        embeddings=embeddings,
        documents=texts,
        metadatas=[record["metadata"] for record in chunk_records],
    )
    return document_id, len(chunk_records)


def ingest_document_sync(file_path: str) -> tuple[str, int]:
    return asyncio.run(ingest_document(file_path))
