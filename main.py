import logging

from fastapi import FastAPI
from redis.asyncio import Redis

from api.routes.chat_routes import router as chat_router
from api.routes.health_routes import router as health_router
from api.routes.search_routes import router as search_router
from api.routes.upload_routes import router as upload_router
from cache.redis_cache import RedisCache
from core.config import get_settings
from core.logging_config import configure_logging
from observability.metrics import MetricsCollector
from observability.request_logger import log_request_timing


settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.middleware("http")(log_request_timing)

redis_client = Redis.from_url(settings.redis_url, decode_responses=False)
app.state.redis_client = redis_client
app.state.cache = RedisCache(redis_client)
app.state.metrics = MetricsCollector()

app.include_router(upload_router, prefix="/documents", tags=["documents"])
app.include_router(search_router, prefix="/documents", tags=["search"])
app.include_router(chat_router, tags=["chat"])
app.include_router(health_router, tags=["health"])


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down application")
    await app.state.redis_client.aclose()
