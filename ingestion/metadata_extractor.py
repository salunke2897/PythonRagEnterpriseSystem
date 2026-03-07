import os
import uuid
from typing import Any


def build_chunk_metadata(document_id: str, source_file: str, page_number: int, chunk_index: int) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "source_file": os.path.basename(source_file),
        "page_number": page_number,
        "chunk_id": f"{document_id}-{page_number}-{chunk_index}-{uuid.uuid4().hex[:8]}",
    }
