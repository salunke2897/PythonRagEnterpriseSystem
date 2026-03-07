import json
import time
from collections.abc import AsyncGenerator
from typing import Any

from cache.redis_cache import RedisCache
from observability.metrics import MetricsCollector
from prompts.chat_prompt import CHAT_HISTORY_PROMPT
from prompts.rag_system_prompt import RAG_SYSTEM_PROMPT
from services.evaluation_service import EvaluationService
from services.llm_service import LLMService
from services.memory_service import MemoryService
from services.rerank_service import RerankService
from services.retrieval_service import RetrievalService


class RAGService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        rerank_service: RerankService,
        llm_service: LLMService,
        memory_service: MemoryService,
        evaluation_service: EvaluationService,
        rerank_top_k: int,
        cache: RedisCache,
        metrics_collector: MetricsCollector,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.rerank_service = rerank_service
        self.llm_service = llm_service
        self.memory_service = memory_service
        self.evaluation_service = evaluation_service
        self.rerank_top_k = rerank_top_k
        self.cache = cache
        self.metrics = metrics_collector

    @staticmethod
    def _build_context(chunks: list[dict[str, Any]]) -> str:
        return "\n\n".join(
            [
                f"[Source: {c['metadata'].get('source_file')} | Page: {c['metadata'].get('page_number')} | Chunk: {c.get('chunk_id')}]\n{c['text']}"
                for c in chunks
            ]
        )

    async def stream_answer(self, question: str, conversation_id: str | None, top_k: int) -> AsyncGenerator[str, None]:
        response_cache_key = f"llm_response:{question}"
        cached_response = await self.cache.get(response_cache_key)
        if cached_response is not None:
            for token in cached_response["answer"].split(" "):
                yield f"data: {json.dumps({'type': 'token', 'content': token + ' '})}\n\n"
            yield f"data: {json.dumps(cached_response)}\n\n"
            return

        retrieval_start = time.perf_counter()
        retrieved_chunks, question_embedding = await self.retrieval_service.retrieve(question, top_k=top_k)
        self.metrics.observe("retrieval_latency_sec", time.perf_counter() - retrieval_start)
        reranked = await self.rerank_service.rerank(question_embedding, retrieved_chunks, top_k=self.rerank_top_k)

        history = []
        if conversation_id:
            history = await self.memory_service.get_recent_messages(conversation_id, limit=5)

        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history]) if history else ""
        context = self._build_context(reranked)
        prompt = RAG_SYSTEM_PROMPT.format(retrieved_context=context, question=question)
        if history_text:
            prompt = f"{CHAT_HISTORY_PROMPT.format(history=history_text)}\n\n{prompt}"

        llm_start = time.perf_counter()
        answer_accumulator = []
        async for token in self.llm_service.stream_complete(prompt):
            answer_accumulator.append(token)
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        self.metrics.observe("llm_latency_sec", time.perf_counter() - llm_start)

        answer = "".join(answer_accumulator)
        self.metrics.increment("llm_output_tokens", len(answer.split()))
        if conversation_id:
            await self.memory_service.save_turn(conversation_id, question, answer)

        metrics = self.evaluation_service.evaluate(question, answer, reranked)
        confidence_score = round(
            (metrics["context_relevance"] + metrics["answer_groundedness"] + metrics["answer_completeness"]) / 3,
            3,
        )
        sources = [
            {
                "document_id": chunk["metadata"].get("document_id"),
                "source_file": chunk["metadata"].get("source_file"),
                "page_number": chunk["metadata"].get("page_number"),
                "chunk_id": chunk.get("chunk_id"),
            }
            for chunk in reranked
        ]

        final_event = {
            "type": "final",
            "answer": answer,
            "sources": sources,
            "confidence_score": confidence_score,
            "evaluation": metrics,
        }
        await self.cache.set(response_cache_key, final_event, ttl=600)
        yield f"data: {json.dumps(final_event)}\n\n"
