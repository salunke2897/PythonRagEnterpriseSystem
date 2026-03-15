from core.config import Settings
from ingestion.ingestion_service import IngestionService


class EmbeddingPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ingestion_service = IngestionService(settings=settings)

    def prepare_chunks(self, file_path: str) -> tuple[str, list[dict]]:
        document_id, chunk_records, _ = self.ingestion_service.process_document(file_path)
        return document_id, chunk_records
