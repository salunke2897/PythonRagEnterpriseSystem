import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.dependencies import get_rag_service
from core.config import get_settings
from models.request_models import ChatRequest
from services.rag_service import RAGService

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest, rag_service: RAGService = Depends(get_rag_service)) -> StreamingResponse:
    settings = get_settings()
    conversation_id = request.conversation_id or str(uuid.uuid4())
    generator = rag_service.stream_answer(question=request.question, conversation_id=conversation_id, top_k=settings.top_k)
    return StreamingResponse(generator, media_type="text/event-stream")
