import json
from typing import Any

from redis.asyncio import Redis


class ConversationMemory:
    def __init__(self, redis_client: Redis, max_history: int = 20) -> None:
        self.redis = redis_client
        self.max_history = max_history

    def _key(self, conversation_id: str) -> str:
        return f"conversation:{conversation_id}"

    async def append_message(self, conversation_id: str, role: str, content: str) -> None:
        key = self._key(conversation_id)
        await self.redis.rpush(key, json.dumps({"role": role, "content": content}))
        await self.redis.ltrim(key, -self.max_history, -1)

    async def get_last_messages(self, conversation_id: str, n: int = 5) -> list[dict[str, Any]]:
        key = self._key(conversation_id)
        records = await self.redis.lrange(key, -n, -1)
        parsed: list[dict[str, Any]] = []
        for item in records:
            text = item.decode("utf-8") if isinstance(item, bytes) else str(item)
            try:
                parsed.append(json.loads(text))
            except Exception:
                continue
        return parsed
