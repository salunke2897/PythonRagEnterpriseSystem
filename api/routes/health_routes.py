from fastapi import APIRouter, Request

from core.config import get_settings
from models.response_models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    settings = get_settings()
    redis_ok = True
    chroma_ok = True

    if settings.cache_backend.lower() == "redis" or settings.memory_backend.lower() == "redis":
        redis_client = getattr(request.app.state, "redis_client", None)
        if redis_client is None:
            redis_ok = False
        else:
            try:
                await redis_client.ping()
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
        dependencies={
            "redis": redis_ok,
            "chroma": chroma_ok,
            "cache_backend": settings.cache_backend,
            "memory_backend": settings.memory_backend,
        },
    )
