from dataclasses import dataclass

import pdfplumber


@dataclass
class PageText:
    page_number: int
    text: str


def extract_pdf_text(file_path: str) -> list[PageText]:
    pages: list[PageText] = []
    with pdfplumber.open(file_path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(PageText(page_number=idx, text=text))
    return pages
