"""Ollama provider: local models served by `ollama serve` (the default, ADR-005)."""

from collections.abc import Sequence

from pydantic import BaseModel, Field

from rag_hive.config import get_settings
from rag_hive.llm.base import LLMConfig, LLMMessage, LLMProvider, LLMResponse, llm_registry


class OllamaConfig(LLMConfig):
    """Which Ollama model to use and where the server listens. Defaults come from `Settings`."""

    model: str = Field(default_factory=lambda: get_settings().llm_model)
    base_url: str = Field(default_factory=lambda: get_settings().ollama_base_url)


@llm_registry.register
class OllamaProvider(LLMProvider):
    """Chat completions through Ollama's HTTP API (`POST /api/chat`)."""

    name = "ollama"
    config_model = OllamaConfig

    async def complete(
        self,
        messages: Sequence[LLMMessage],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Return the model's reply. See `LLMProvider.complete`."""
        raise NotImplementedError

    async def complete_structured[M: BaseModel](
        self,
        messages: Sequence[LLMMessage],
        schema: type[M],
        *,
        temperature: float = 0.0,
    ) -> M:
        """Return the reply parsed into `schema`. See `LLMProvider.complete_structured`."""
        raise NotImplementedError
