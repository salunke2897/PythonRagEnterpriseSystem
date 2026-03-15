from typing import Any

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    chunks_created: int


class UploadedFileItem(BaseModel):
    file_name: str
    file_size_bytes: int
    modified_at: str


class UploadedFilesResponse(BaseModel):
    files: list[UploadedFileItem]


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    source_file: str
    page_number: int
    vector_score: float
    keyword_score: float
    final_score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]


class HealthResponse(BaseModel):
    status: str
    version: str
    dependencies: dict[str, Any]
