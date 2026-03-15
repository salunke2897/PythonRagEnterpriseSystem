import hashlib
import re
import uuid

from ingestion.ingestion_types import ParsedPage
from utils.token_counter import count_tokens


class SemanticChunker:
    """Chunk by sections/headings and bounded token windows."""

    def __init__(self, min_tokens: int = 600, max_tokens: int = 800, model: str = "gpt-4.1-mini") -> None:
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.model = model

    @staticmethod
    def _split_sections(text: str) -> list[tuple[str, str]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        sections: list[tuple[str, str]] = []
        current_heading = "General"
        buffer: list[str] = []

        heading_pattern = re.compile(r"^([A-Z][A-Za-z0-9\s\-]{2,}|\d+(\.\d+)*\s+.+)$")
        for line in lines:
            if heading_pattern.match(line) and len(line.split()) <= 14:
                if buffer:
                    sections.append((current_heading, "\n".join(buffer)))
                    buffer = []
                current_heading = line
            else:
                buffer.append(line)
        if buffer:
            sections.append((current_heading, "\n".join(buffer)))
        return sections or [("General", text)]

    def chunk_pages(self, document_id: str, source_file: str, pages: list[ParsedPage]) -> list[dict]:
        chunks: list[dict] = []
        seen_hashes: set[str] = set()

        for page in pages:
            for section, body in self._split_sections(page.text):
                paragraphs = [p.strip() for p in body.split("\n") if p.strip()]
                current: list[str] = []

                def flush(chunk_type: str = "section") -> None:
                    if not current:
                        return
                    chunk_text = "\n".join(current).strip()
                    if not chunk_text:
                        return
                    chunk_hash = hashlib.sha1(chunk_text.lower().encode("utf-8")).hexdigest()
                    if chunk_hash in seen_hashes:
                        return
                    seen_hashes.add(chunk_hash)
                    chunk_id = f"{document_id}-{page.page_number}-{uuid.uuid4().hex[:8]}"
                    chunks.append(
                        {
                            "id": chunk_id,
                            "text": chunk_text,
                            "metadata": {
                                "document_id": document_id,
                                "page_number": page.page_number,
                                "section": section,
                                "chunk_type": chunk_type,
                                "source_file": source_file,
                                "chunk_id": chunk_id,
                            },
                        }
                    )

                for para in paragraphs:
                    trial = "\n".join([*current, para])
                    token_len = count_tokens(trial, model=self.model)
                    if token_len > self.max_tokens and current:
                        flush()
                        current = [para]
                    else:
                        current.append(para)

                    if count_tokens("\n".join(current), model=self.model) >= self.min_tokens:
                        flush()
                        current = []

                flush()

        return chunks
