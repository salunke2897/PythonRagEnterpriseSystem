import logging

from ingestion.ingestion_types import ParsedDocument
from ingestion.parsers.pdfplumber_parser import PDFPlumberParser
from ingestion.parsers.pymupdf_parser import PyMuPDFParser

logger = logging.getLogger(__name__)


class FallbackParser:
    """Parse PDF in resilient order: PyMuPDF -> pdfplumber -> optional Apache Tika."""

    def __init__(self) -> None:
        self.pymupdf = PyMuPDFParser()
        self.pdfplumber = PDFPlumberParser()

    def parse(self, file_path: str, allow_empty_text: bool = False) -> ParsedDocument:
        for parser_name, parser in (("pymupdf", self.pymupdf), ("pdfplumber", self.pdfplumber)):
            try:
                parsed = parser.parse(file_path)
                if allow_empty_text or any(page.text.strip() for page in parsed.pages):
                    return parsed
            except Exception:
                logger.exception("parser_failed", extra={"extra": {"parser": parser_name}})

        tika_result = self._parse_with_tika(file_path)
        if tika_result:
            return tika_result

        raise ValueError("All parser fallbacks failed")

    def _parse_with_tika(self, file_path: str) -> ParsedDocument | None:
        try:
            from tika import parser as tika_parser  # type: ignore

            result = tika_parser.from_file(file_path)
            text = (result or {}).get("content") or ""
            if not text.strip():
                return None
            from ingestion.ingestion_types import ParsedPage

            return ParsedDocument(parser_used="tika", pages=[ParsedPage(page_number=1, text=text)])
        except Exception:
            logger.info("tika_unavailable_or_failed")
            return None
