"""OpenAI-compatible API client with async concurrency and retry."""

import asyncio
import logging
from dataclasses import dataclass
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


@dataclass
class InferenceConfig:
    max_tokens: int = 4096
    temperature: float = 0.0
    top_p: float = 1.0
    n_samples: int = 1
    timeout: int = 120
    max_concurrency: int = 8
    max_retries: int = 3


class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str, config: InferenceConfig):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=300)
        self.model = model
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrency)

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a single response with retry logic."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        for attempt in range(self.config.max_retries):
            try:
                async with self.semaphore:
                    response = await asyncio.wait_for(
                        self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            max_tokens=self.config.max_tokens,
                            temperature=self.config.temperature,
                            top_p=self.config.top_p,
                        ),
                        timeout=self.config.timeout,
                    )
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.config.max_retries} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        return ""

    async def generate_batch(self, prompts: list[tuple[str, str]]) -> list[str]:
        """Generate responses for a batch of (system_prompt, user_prompt) pairs."""
        tasks = [self.generate(sys, usr) for sys, usr in prompts]
        return await asyncio.gather(*tasks)
