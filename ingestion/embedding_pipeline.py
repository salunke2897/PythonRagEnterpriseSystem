import uuid

from core.config import Settings
from ingestion.metadata_extractor import build_chunk_metadata
from ingestion.pdf_loader import extract_pdf_text
from ingestion.text_chunker import chunk_text
from ingestion.text_cleaner import clean_text


class EmbeddingPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def prepare_chunks(self, file_path: str) -> tuple[str, list[dict]]:
        document_id = str(uuid.uuid4())
        pages = extract_pdf_text(file_path)

        chunk_records: list[dict] = []
        for page in pages:
            cleaned = clean_text(page.text)
            if not cleaned:
                continue
            chunks = chunk_text(
                cleaned,
                chunk_size=self.settings.chunk_size,
                overlap=self.settings.chunk_overlap,
                model=self.settings.embedding_model,
            )
            for idx, chunk in enumerate(chunks):
                metadata = build_chunk_metadata(document_id, file_path, page.page_number, idx)
                chunk_records.append({"id": metadata["chunk_id"], "text": chunk, "metadata": metadata})

        return document_id, chunk_records
