"""Application settings, loaded from the environment and the repo-root `.env`.

Every tunable value lives here. Code receives a `Settings` instance from `get_settings()`
(injected with FastAPI `Depends` in routes) instead of reading the environment itself.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]
"""Repository root (`backend/src/rag_hive/config.py` is three levels below it)."""

type LLMProviderName = Literal["ollama"]
"""Registry names (`llm_registry`) of the LLM providers `Settings` accepts.

Local only: no paid API at runtime (ADR-005).
"""

type EmbeddingProviderName = Literal["sentence-transformers"]
"""Registry names (`embedder_registry`) of the embedders `Settings` accepts.

Local only: no paid API at runtime (ADR-005).
"""

type LogLevel = Literal["critical", "error", "warning", "info", "debug"]
"""Log levels accepted by uvicorn."""


class Settings(BaseSettings):
    """Runtime configuration. Field names map to upper-case environment variables."""

    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        frozen=True,
    )

    backend_host: str = "127.0.0.1"
    backend_port: int = Field(default=8000, ge=1, le=65535)
    backend_reload: bool = False
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    log_level: LogLevel = "info"

    llm_provider: LLMProviderName = "ollama"
    llm_model: str = "qwen3:8b"
    ollama_base_url: str = "http://127.0.0.1:11434"
    embedding_provider: EmbeddingProviderName = "sentence-transformers"
    embedding_model: str = "BAAI/bge-m3"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, read once on first call."""
    return Settings()
