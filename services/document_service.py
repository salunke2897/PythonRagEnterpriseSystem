import logging

from ingestion.embedding_pipeline import EmbeddingPipeline
from services.embedding_service import EmbeddingService
from vectorstore.vector_store_interface import VectorStoreInterface

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self,
        pipeline: EmbeddingPipeline,
        embedding_service: EmbeddingService,
        vector_store: VectorStoreInterface,
    ) -> None:
        self.pipeline = pipeline
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    @staticmethod
    def _embed_with_sentence_transformers(texts: list[str]) -> list[list[float]]:
        from sentence_transformers import SentenceTransformer  # type: ignore

        model = SentenceTransformer("all-MiniLM-L6-v2")
        vectors = model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]

    async def ingest_pdf(self, file_path: str) -> tuple[str, int]:
        document_id, chunk_records = self.pipeline.prepare_chunks(file_path)
        if not chunk_records:
            return document_id, 0

        texts = [record["text"] for record in chunk_records]
        try:
            embeddings = await self.embedding_service.embed_batch(texts)
        except Exception:
            logger.exception("openai_embedding_failed_fallback_to_sentence_transformer")
            embeddings = self._embed_with_sentence_transformers(texts)

        await self.vector_store.upsert(
            ids=[record["id"] for record in chunk_records],
            embeddings=embeddings,
            documents=texts,
            metadatas=[record["metadata"] for record in chunk_records],
        )
        return document_id, len(chunk_records)
