from tenacity import retry, stop_after_attempt, wait_exponential

import pdfplumber

from ingestion.ingestion_types import ParsedDocument, ParsedPage


class PDFPlumberParser:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
    def parse(self, file_path: str) -> ParsedDocument:
        pages: list[ParsedPage] = []
        with pdfplumber.open(file_path) as pdf:
            for index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                words = page.extract_words() or []
                pages.append(ParsedPage(page_number=index, text=text, words=words))
        return ParsedDocument(parser_used="pdfplumber", pages=pages)
