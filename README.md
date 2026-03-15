# Enterprise RAG System (FastAPI + OpenAI + ChromaDB)

Production-style modular Retrieval-Augmented Generation platform for PDF knowledge retrieval with grounded answers and anti-hallucination prompting.

## Features

- PDF upload and ingestion pipeline (extract → clean → chunk → embed → index)
- OpenAI embeddings and generation
- Chroma vector store abstraction (future Pinecone swap)
- Hybrid retrieval (vector + BM25)
- Reranking step (top 10 → top 5)
- Grounded anti-hallucination prompt
- Conversational memory in Redis or in-memory mode
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

Windows (PowerShell):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment template:

```bash
Copy-Item .env.example .env
```

4. Set at minimum:

- `OPENAI_API_KEY`
- `CHAT_MODEL`
- `EMBEDDING_MODEL`

For local development without Redis, set:

- `CACHE_BACKEND=memory`
- `MEMORY_BACKEND=memory`

If using Redis backend, also set:

- `REDIS_URL`

5. Start Redis locally only when `CACHE_BACKEND=redis` or `MEMORY_BACKEND=redis`.

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
- `CACHE_BACKEND` (`redis` or `memory`)
- `MEMORY_BACKEND` (`redis` or `memory`)
- `CHROMA_PERSIST_DIR`
- `UPLOAD_DIR`
- `MAX_PDF_SIZE_MB`
- `MAX_TOKENS`
- `LOG_LEVEL`

## Advanced PDF Extraction (New)

The ingestion pipeline is upgraded for real-world enterprise PDFs (digital + scanned) while keeping the same project architecture.

### Pipeline Flow

`PDF Upload -> PDF Type Detection -> Parser Fallback -> OCR (if scanned) -> Layout Detection -> Table Extraction -> Image Extraction -> Header/Footer Cleaning -> Semantic Chunking -> Embedding -> Vector Index`

### Ingestion Modules Added

- `ingestion/detectors/pdf_type_detector.py`
- `ingestion/parsers/pymupdf_parser.py`
- `ingestion/parsers/pdfplumber_parser.py`
- `ingestion/parsers/fallback_parser.py`
- `ingestion/ocr/paddle_ocr.py`
- `ingestion/layout/layout_detector.py`
- `ingestion/tables/table_extractor.py`
- `ingestion/images/image_extractor.py`
- `ingestion/cleaners/text_cleaner.py`
- `ingestion/chunking/semantic_chunker.py`
- `ingestion/ingestion_service.py`

### Extraction Behavior

- **PDF type detection**: identifies digital vs scanned PDFs.
- **Parser fallback**: tries PyMuPDF first, then pdfplumber, then optional Tika fallback.
- **Scanned support**: allows empty parser text for scanned docs and continues with OCR.
- **OCR**: PaddleOCR + OpenCV preprocessing for image-based pages.
- **Layout support**: layout block detection (title/paragraph/list/table/figure).
- **Tables**: extracted via Camelot and converted to markdown for LLM-friendly context.
- **Images**: metadata extracted (page, size, extension, dimensions).
- **Cleaner**: repeated header/footer line removal across pages.
- **Semantic chunking**: section-aware chunks (~600–800 tokens) with deduplication.

### Chunk Metadata

Each chunk includes:

- `document_id`
- `page_number`
- `section`
- `chunk_type`
- `source_file`
- `chunk_id`

### Observability for Ingestion

Ingestion logs/metrics now track:

- parser used
- OCR usage
- chunks created
- ingestion time
- failure events

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

