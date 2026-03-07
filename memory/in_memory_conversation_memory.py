from collections import defaultdict
from typing import Any


class InMemoryConversationMemory:
    def __init__(self, max_history: int = 20) -> None:
        self.max_history = max_history
        self._store: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async def append_message(self, conversation_id: str, role: str, content: str) -> None:
        self._store[conversation_id].append({"role": role, "content": content})
        self._store[conversation_id] = self._store[conversation_id][-self.max_history :]

    async def get_last_messages(self, conversation_id: str, n: int = 5) -> list[dict[str, Any]]:
        return self._store.get(conversation_id, [])[-n:]
