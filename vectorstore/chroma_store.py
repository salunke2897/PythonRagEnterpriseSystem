from typing import Any

import chromadb

from vectorstore.vector_store_interface import VectorStoreInterface


class ChromaStore(VectorStoreInterface):
    def __init__(self, persist_dir: str, collection_name: str = "rag_documents") -> None:
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})

    async def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    async def query(self, embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        results = self.collection.query(query_embeddings=[embedding], n_results=top_k, include=["documents", "metadatas", "distances"])
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        response: list[dict[str, Any]] = []
        for text, metadata, dist in zip(docs, metas, distances):
            vector_score = 1 - float(dist)
            response.append(
                {
                    "chunk_id": metadata.get("chunk_id"),
                    "text": text,
                    "metadata": metadata,
                    "vector_score": max(0.0, vector_score),
                }
            )
        return response

    async def get_all_documents(self) -> list[dict[str, Any]]:
        records = self.collection.get(include=["documents", "metadatas"])
        docs = records.get("documents", [])
        metas = records.get("metadatas", [])
        ids = records.get("ids", [])
        merged: list[dict[str, Any]] = []
        for _id, doc, meta in zip(ids, docs, metas):
            merged.append({"chunk_id": _id, "text": doc, "metadata": meta})
        return merged
