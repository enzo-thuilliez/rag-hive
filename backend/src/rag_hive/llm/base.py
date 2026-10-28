"""LLM provider interface and registry.

Agents never build an SDK client themselves: they get an `LLMProvider` through `create_llm`,
which picks the provider named by `Settings.llm_provider`. Runtime providers are local only
(ADR-005).
"""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

from rag_hive.config import Settings
from rag_hive.core.component import Component, ComponentConfig
from rag_hive.core.registry import Registry

type Role = Literal["system", "user", "assistant"]
"""Author of a chat message."""


class LLMMessage(BaseModel):
    """One chat message sent to the model."""

    role: Role
    content: str


class LLMResponse(BaseModel):
    """A completion and its token usage."""

    text: str
    model: str = Field(description="Model that produced the text, as reported by the provider.")
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)


class LLMConfig(ComponentConfig):
    """Options shared by every LLM provider. Subclass per provider."""


class LLMProvider(Component):
    """A chat model the agents talk to."""

    @abstractmethod
    async def complete(
        self,
        messages: Sequence[LLMMessage],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Return the model's reply to `messages`.

        Args:
            messages: The conversation, oldest first.
            temperature: Sampling temperature; 0 for the most deterministic output.
            max_tokens: Cap on generated tokens, or None for the provider's default.
        """

    @abstractmethod
    async def complete_structured[M: BaseModel](
        self,
        messages: Sequence[LLMMessage],
        schema: type[M],
        *,
        temperature: float = 0.0,
    ) -> M:
        """Return the model's reply parsed into `schema`.

        The provider constrains generation to the model's JSON Schema where it can (Ollama's
        `format` parameter) and validates the result.

        Raises:
            pydantic.ValidationError: If the reply does not match `schema`.
        """


llm_registry: Registry[LLMProvider] = Registry("llm provider")
"""Every registered LLM provider, by name. `Settings.llm_provider` names one of them."""


def create_llm(settings: Settings) -> LLMProvider:
    """Build the LLM provider selected by `settings.llm_provider`, configured from `settings`.

    Raises:
        UnknownComponentError: If no provider is registered under that name.
    """
    raise NotImplementedError
