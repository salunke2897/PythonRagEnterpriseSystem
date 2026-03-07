import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from api.routes.chat_routes import router as chat_router
from api.routes.health_routes import router as health_router
from api.routes.search_routes import router as search_router
from api.routes.upload_routes import router as upload_router
from cache.in_memory_cache import InMemoryCache
from cache.redis_cache import RedisCache
from core.config import get_settings
from core.logging_config import configure_logging
from memory.conversation_memory import ConversationMemory
from memory.in_memory_conversation_memory import InMemoryConversationMemory
from observability.metrics import MetricsCollector
from observability.request_logger import log_request_timing


settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.middleware("http")(log_request_timing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.redis_client = None
if settings.cache_backend.lower() == "memory":
    app.state.cache = InMemoryCache()
else:
    redis_client = Redis.from_url(settings.redis_url, decode_responses=False)
    app.state.redis_client = redis_client
    app.state.cache = RedisCache(redis_client)

if settings.memory_backend.lower() == "memory":
    app.state.memory_store = InMemoryConversationMemory()
else:
    if app.state.redis_client is None:
        redis_client = Redis.from_url(settings.redis_url, decode_responses=False)
        app.state.redis_client = redis_client
    app.state.memory_store = ConversationMemory(app.state.redis_client)

app.state.metrics = MetricsCollector()

app.include_router(upload_router, prefix="/documents", tags=["documents"])
app.include_router(search_router, prefix="/documents", tags=["search"])
app.include_router(chat_router, tags=["chat"])
app.include_router(health_router, tags=["health"])


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down application")
    if app.state.redis_client is not None:
        await app.state.redis_client.aclose()
