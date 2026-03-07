from fastapi import APIRouter, Request

from core.config import get_settings
from models.response_models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    settings = get_settings()
    redis_ok = True
    chroma_ok = True
    try:
        await request.app.state.redis_client.ping()
    except Exception:
        redis_ok = False

    container = getattr(request.app.state, "service_container", None)
    if container is not None:
        try:
            _ = container["retrieval_service"].vector_store
        except Exception:
            chroma_ok = False

    return HealthResponse(
        status="ok" if redis_ok and chroma_ok else "degraded",
        version=settings.app_version,
        dependencies={"redis": redis_ok, "chroma": chroma_ok},
    )
