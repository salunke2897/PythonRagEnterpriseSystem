import asyncio
import logging
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from core.config import Settings, get_settings
from ingestion.chunking.semantic_chunker import SemanticChunker
from ingestion.cleaners.text_cleaner import AdvancedTextCleaner
from ingestion.detectors.pdf_type_detector import PDFTypeDetector
from ingestion.layout.layout_detector import LayoutDetector
from ingestion.ocr.paddle_ocr import PaddleOCRExtractor
from ingestion.parsers.fallback_parser import FallbackParser
from ingestion.tables.table_extractor import TableExtractor
from ingestion.images.image_extractor import ImageExtractor
from observability.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, settings: Settings, metrics: MetricsCollector | None = None) -> None:
        self.settings = settings
        self.metrics = metrics
        self.detector = PDFTypeDetector()
        self.parser = FallbackParser()
        self.ocr = PaddleOCRExtractor()
        self.layout = LayoutDetector()
        self.table_extractor = TableExtractor()
        self.image_extractor = ImageExtractor()
        self.cleaner = AdvancedTextCleaner()
        self.chunker = SemanticChunker(min_tokens=600, max_tokens=800, model=settings.embedding_model)

    def _observe(self, metric_name: str, value: float) -> None:
        if self.metrics:
            self.metrics.observe(metric_name, value)

    def _increment(self, metric_name: str, value: int = 1) -> None:
        if self.metrics:
            self.metrics.increment(metric_name, value)

    def _detect_layout_parallel(self, pages) -> None:
        def _detect(page):
            page.layout_blocks = self.layout.detect_from_text(page.text)
            return page

        with ThreadPoolExecutor(max_workers=min(8, max(1, len(pages)))) as executor:
            list(executor.map(_detect, pages))

    def process_document(self, file_path: str) -> tuple[str, list[dict], dict]:
        start = time.perf_counter()
        document_id = str(uuid.uuid4())
        source_file = os.path.basename(file_path)

        pdf_type = self.detector.detect(file_path)
        parsed = self.parser.parse(file_path, allow_empty_text=(pdf_type == "scanned"))
        self._increment(f"ingestion.parser.{parsed.parser_used}")

        ocr_used = False
        if pdf_type == "scanned":
            ocr_used = True
            self._increment("ingestion.ocr.used")
            ocr_output = self.ocr.extract(file_path)
            for page in parsed.pages:
                if not page.text.strip() and page.page_number in ocr_output:
                    page.text = ocr_output[page.page_number]["text"]

        self._detect_layout_parallel(parsed.pages)

        table_markdown = self.table_extractor.extract_markdown_tables(file_path)
        image_metadata = self.image_extractor.extract_image_metadata(file_path)
        cleaned_pages = self.cleaner.remove_headers_footers(parsed.pages)

        for page in cleaned_pages:
            if page.page_number in table_markdown and table_markdown[page.page_number]:
                page.text = f"{page.text}\n\nDetected Tables:\n" + "\n\n".join(table_markdown[page.page_number])

        chunks = self.chunker.chunk_pages(document_id=document_id, source_file=source_file, pages=cleaned_pages)

        elapsed = time.perf_counter() - start
        self._observe("ingestion_latency_sec", elapsed)
        self._increment("ingestion.chunks_created", len(chunks))

        stats = {
            "document_id": document_id,
            "parser_used": parsed.parser_used,
            "pdf_type": pdf_type,
            "ocr_used": ocr_used,
            "tables_detected": sum(len(v) for v in table_markdown.values()),
            "images_detected": len(image_metadata),
            "chunks_created": len(chunks),
            "ingestion_time_sec": elapsed,
        }
        logger.info("document_ingested", extra={"extra": stats})
        return document_id, chunks, stats


async def process_document(file_path: str, settings: Settings | None = None, metrics: MetricsCollector | None = None):
    app_settings = settings or get_settings()
    service = IngestionService(settings=app_settings, metrics=metrics)
    return await asyncio.to_thread(service.process_document, file_path)
