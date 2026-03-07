from typing import Any

from vectorstore.vector_store_interface import VectorStoreInterface


class VectorSearch:
    def __init__(self, store: VectorStoreInterface) -> None:
        self.store = store

    async def search(self, query_embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        return await self.store.query(query_embedding, top_k=top_k)
