import fitz


class PDFTypeDetector:
    """Detect if a PDF is digital or scanned by checking extractable text ratio."""

    def __init__(self, min_chars_per_page: int = 20, digital_page_ratio_threshold: float = 0.3) -> None:
        self.min_chars_per_page = min_chars_per_page
        self.digital_page_ratio_threshold = digital_page_ratio_threshold

    def detect(self, file_path: str) -> str:
        with fitz.open(file_path) as doc:
            if len(doc) == 0:
                return "scanned"

            pages_with_text = 0
            for page in doc:
                text = page.get_text("text") or ""
                if len(text.strip()) >= self.min_chars_per_page:
                    pages_with_text += 1

            ratio = pages_with_text / max(len(doc), 1)
            return "digital" if ratio >= self.digital_page_ratio_threshold else "scanned"
