from ingestion.embedding_pipeline import EmbeddingPipeline
from services.embedding_service import EmbeddingService
from vectorstore.vector_store_interface import VectorStoreInterface


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

    async def ingest_pdf(self, file_path: str) -> tuple[str, int]:
        document_id, chunk_records = self.pipeline.prepare_chunks(file_path)
        if not chunk_records:
            return document_id, 0

        texts = [record["text"] for record in chunk_records]
        embeddings = await self.embedding_service.embed_batch(texts)

        await self.vector_store.upsert(
            ids=[record["id"] for record in chunk_records],
            embeddings=embeddings,
            documents=texts,
            metadatas=[record["metadata"] for record in chunk_records],
        )
        return document_id, len(chunk_records)
