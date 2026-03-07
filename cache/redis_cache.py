import json
from typing import Any

from redis.asyncio import Redis


class RedisCache:
    def __init__(self, redis_client: Redis, default_ttl: int = 3600) -> None:
        self.redis = redis_client
        self.default_ttl = default_ttl

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        await self.redis.set(key, json.dumps(value), ex=ttl or self.default_ttl)
