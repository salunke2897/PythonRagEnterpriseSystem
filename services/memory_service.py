from typing import Any

class MemoryService:
    def __init__(self, memory_store: Any) -> None:
        self.memory_store = memory_store

    async def save_turn(self, conversation_id: str, question: str, answer: str) -> None:
        await self.memory_store.append_message(conversation_id, "user", question)
        await self.memory_store.append_message(conversation_id, "assistant", answer)

    async def get_recent_messages(self, conversation_id: str, limit: int = 5) -> list[dict[str, Any]]:
        return await self.memory_store.get_last_messages(conversation_id, limit)
