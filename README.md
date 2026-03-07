# Enterprise RAG System (FastAPI + OpenAI + ChromaDB)

Production-style modular Retrieval-Augmented Generation platform for PDF knowledge retrieval with grounded answers and anti-hallucination prompting.

## Features

- PDF upload and ingestion pipeline (extract → clean → chunk → embed → index)
- OpenAI embeddings and generation
- Chroma vector store abstraction (future Pinecone swap)
- Hybrid retrieval (vector + BM25)
- Reranking step (top 10 → top 5)
- Grounded anti-hallucination prompt
- Conversational memory in Redis
- SSE token streaming response
- Caching (embeddings, retrieval, LLM responses)
- Structured logging, request tracing, basic metrics
- Evaluation metrics (relevance, groundedness, completeness)

## Project Structure

```
rag-enterprise-system/
├── api/
│   └── routes/
├── cache/
├── core/
├── ingestion/
├── memory/
├── models/
├── observability/
├── prompts/
├── reranking/
├── retrieval/
├── services/
├── tests/
├── utils/
├── vectorstore/
├── workers/
├── main.py
├── requirements.txt
└── .env.example
```

## Setup

1. Create and activate virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment template:

```bash
cp .env.example .env
```

4. Set at minimum:

- `OPENAI_API_KEY`
- `CHAT_MODEL`
- `EMBEDDING_MODEL`
- `REDIS_URL`

5. Start Redis locally.

6. Run API:

```bash
uvicorn main:app --reload
```

## Environment Variables

- `OPENAI_API_KEY`
- `CHAT_MODEL`
- `EMBEDDING_MODEL`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`
- `TOP_K`
- `RERANK_TOP_K`
- `REDIS_URL`
- `CHROMA_PERSIST_DIR`
- `UPLOAD_DIR`
- `MAX_PDF_SIZE_MB`
- `MAX_TOKENS`
- `LOG_LEVEL`

## API Endpoints

### `POST /documents/upload`

Upload and index a PDF document.

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf"
```

Response:

```json
{
  "document_id": "...",
  "chunks_created": 42
}
```

### `POST /chat`

Streaming SSE response (`text/event-stream`).

```bash
curl -N -X POST "http://127.0.0.1:8000/chat" \
  -H "accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{"question":"What does the document explain?","conversation_id":"conv-123"}'
```

Events:
- `type=token` for token chunks
- `type=final` with full payload: `answer`, `sources`, `confidence_score`, `evaluation`

### `GET /documents/search`

```bash
curl "http://127.0.0.1:8000/documents/search?q=data%20retention&top_k=10"
```

### `GET /health`

```bash
curl "http://127.0.0.1:8000/health"
```

## Retrieval Design

- Vector search from Chroma
- Keyword search with BM25 (`rank-bm25`)
- Hybrid score:

```
final_score = 0.7 * vector_score + 0.3 * keyword_score
```

## Prompt Grounding

System prompt enforces strict context grounding:

> You MUST answer using only the information in the context.
> If missing, respond: "I cannot find the answer in the provided documents."

## Scalability Approach

- **Docker**: package each module as independent service containers
- **Kubernetes**: autoscale API pods and independent ingestion workers
- **Redis Cluster**: scale cache and conversation memory horizontally
- **External Vector DB**: replace `ChromaStore` with Pinecone implementation using `VectorStoreInterface`
- **Message Queue**: route heavy ingestion to Celery/RQ/Kafka workers via `workers/ingestion_worker.py`

## Security

- Upload MIME/type and extension validation
- Max PDF size enforcement
- Input length constraints via Pydantic
- Sanitized file name handling for persisted uploads

## Notes

- For production, add authN/authZ, rate limiting, secret manager integration, and OpenTelemetry export.
- Reranking is implemented with embedding similarity; can be upgraded to cross-encoder models.
