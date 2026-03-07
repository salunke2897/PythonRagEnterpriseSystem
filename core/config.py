from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise RAG System"
    app_version: str = "1.0.0"

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    chat_model: str = Field(default="gpt-4.1-mini", alias="CHAT_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")

    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")
    top_k: int = Field(default=10, alias="TOP_K")
    rerank_top_k: int = Field(default=5, alias="RERANK_TOP_K")
    max_tokens: int = Field(default=600, alias="MAX_TOKENS")

    cache_backend: str = Field(default="redis", alias="CACHE_BACKEND")
    memory_backend: str = Field(default="redis", alias="MEMORY_BACKEND")

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    chroma_persist_dir: str = Field(default="./data/chroma", alias="CHROMA_PERSIST_DIR")
    upload_dir: str = Field(default="./data/uploads", alias="UPLOAD_DIR")
    max_pdf_size_mb: int = Field(default=20, alias="MAX_PDF_SIZE_MB")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    def ensure_directories(self) -> None:
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.chroma_persist_dir).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
