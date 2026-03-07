from collections.abc import AsyncGenerator

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import Settings


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def complete(self, prompt: str) -> str:
        response = await self.client.responses.create(
            model=self.settings.chat_model,
            input=prompt,
            temperature=0,
            max_output_tokens=self.settings.max_tokens,
        )
        return response.output_text

    async def stream_complete(self, prompt: str) -> AsyncGenerator[str, None]:
        stream = await self.client.responses.create(
            model=self.settings.chat_model,
            input=prompt,
            temperature=0,
            max_output_tokens=self.settings.max_tokens,
            stream=True,
        )
        async for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta
