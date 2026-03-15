from tenacity import retry, stop_after_attempt, wait_exponential

import fitz

from ingestion.ingestion_types import ParsedDocument, ParsedPage


class PyMuPDFParser:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
    def parse(self, file_path: str) -> ParsedDocument:
        pages: list[ParsedPage] = []
        with fitz.open(file_path) as doc:
            for index, page in enumerate(doc, start=1):
                words = page.get_text("words") or []
                text = page.get_text("text") or ""
                word_payload = [
                    {"x0": w[0], "y0": w[1], "x1": w[2], "y1": w[3], "text": w[4], "block": w[5], "line": w[6]}
                    for w in words
                ]
                pages.append(ParsedPage(page_number=index, text=text, words=word_payload))
        return ParsedDocument(parser_used="pymupdf", pages=pages)
