import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from core.exceptions import ValidationException


def validate_pdf_upload(file: UploadFile, max_size_mb: int) -> None:
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise ValidationException("Only PDF files are allowed.")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise ValidationException("File extension must be .pdf")

    max_size_bytes = max_size_mb * 1024 * 1024
    content_length = file.size or 0
    if content_length and content_length > max_size_bytes:
        raise ValidationException(f"File exceeds max size of {max_size_mb} MB")


async def save_upload_file(file: UploadFile, upload_dir: str) -> str:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{os.path.basename(file.filename or 'document.pdf')}"
    target_path = Path(upload_dir) / safe_name
    content = await file.read()
    with open(target_path, "wb") as out_file:
        out_file.write(content)
    return str(target_path)
