import os
from dataclasses import dataclass
from typing import Any

from agno.models.openai import OpenAIChat

from lkthink_agent.providers.base import BaseLLMProvider


@dataclass(frozen=True, slots=True)
class DeepSeekConfig:
    api_key: str
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"
    temperature: float = 0.2
    max_tokens: int | None = None
    timeout: float = 60.0

    def __post_init__(self):
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY não configurada.")

        if not self.model:
            raise ValueError("Modelo DeepSeek não informado.")

        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature deve estar entre 0 e 2.")

        if self.timeout <= 0:
            raise ValueError("Timeout deve ser maior que zero.")

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            base_url=os.getenv(
                "DEEPSEEK_BASE_URL",
                "https://api.deepseek.com",
            ),
            temperature=float(
                os.getenv("DEEPSEEK_TEMPERATURE", "0.2")
            ),
            max_tokens=(
                int(os.environ["DEEPSEEK_MAX_TOKENS"])
                if os.getenv("DEEPSEEK_MAX_TOKENS")
                else None
            ),
            timeout=float(
                os.getenv("DEEPSEEK_TIMEOUT", "60")
            ),
        )


class DeepSeekProvider(BaseLLMProvider):
    """Adapter interno para DeepSeek através da API compatível com OpenAI."""

    def __init__(self, config: DeepSeekConfig):
        self.config = config

    def build_model(self) -> Any:
        return OpenAIChat(
            id=self.config.model,
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            timeout=self.config.timeout,
            max_retries=0,
        )