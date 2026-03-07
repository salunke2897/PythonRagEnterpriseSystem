from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import Settings


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def embed_text(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(model=self.settings.embedding_model, input=text)
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(model=self.settings.embedding_model, input=texts)
        return [item.embedding for item in response.data]
