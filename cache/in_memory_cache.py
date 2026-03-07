import time
from typing import Any


class InMemoryCache:
    def __init__(self, default_ttl: int = 3600) -> None:
        self.default_ttl = default_ttl
        self._store: dict[str, tuple[float, Any]] = {}

    async def get(self, key: str) -> Any | None:
        record = self._store.get(key)
        if record is None:
            return None

        expires_at, value = record
        if expires_at < time.time():
            self._store.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        lifetime = ttl or self.default_ttl
        self._store[key] = (time.time() + lifetime, value)
