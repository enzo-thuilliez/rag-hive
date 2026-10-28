"""LLM providers the agents call, chosen by `Settings.llm_provider`.

Local only (ADR-005): Ollama is the one provider and the default. No paid provider is
implemented. Importing this package registers every provider in `llm_registry`.
"""

from rag_hive.llm.base import (
    LLMConfig,
    LLMMessage,
    LLMProvider,
    LLMResponse,
    create_llm,
    llm_registry,
)
from rag_hive.llm.ollama import OllamaConfig, OllamaProvider

__all__ = [
    "LLMConfig",
    "LLMMessage",
    "LLMProvider",
    "LLMResponse",
    "OllamaConfig",
    "OllamaProvider",
    "create_llm",
    "llm_registry",
]
