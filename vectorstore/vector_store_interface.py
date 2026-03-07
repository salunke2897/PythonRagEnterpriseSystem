from abc import ABC, abstractmethod
from typing import Any


class VectorStoreInterface(ABC):
    @abstractmethod
    async def upsert(self, ids: list[str], embeddings: list[list[float]], documents: list[str], metadatas: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def query(self, embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_documents(self) -> list[dict[str, Any]]:
        raise NotImplementedError
