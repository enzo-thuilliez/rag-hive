"""Local embeddings through sentence-transformers, BGE-M3 by default (ADR-005)."""

from collections.abc import Sequence

from pydantic import Field

from rag_hive.config import get_settings
from rag_hive.embedders.base import Embedder, EmbedderConfig, embedder_registry


class SentenceTransformerConfig(EmbedderConfig):
    """Which model to load and how to run it. The default model comes from `Settings`."""

    model: str = Field(
        default_factory=lambda: get_settings().embedding_model,
        description="Hugging Face model id, `BAAI/bge-m3` by default.",
    )
    batch_size: int = Field(default=16, ge=1)
    normalize: bool = Field(default=True, description="L2-normalize vectors (cosine = dot).")
    device: str | None = Field(default=None, description="`cpu`, `cuda`... None: auto-detect.")


@embedder_registry.register
class SentenceTransformerEmbedder(Embedder):
    """Dense embeddings from a local sentence-transformers model.

    BGE-M3 (the default) returns 1024-dimension vectors and needs no query prefix. The model is
    downloaded on first use and loaded once per instance; encoding runs in a worker thread so
    it does not block the event loop.
    """

    name = "sentence-transformers"
    config_model = SentenceTransformerConfig

    @property
    def dimension(self) -> int:
        """Vector length reported by the loaded model."""
        raise NotImplementedError

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed passages. See `Embedder.embed_documents`."""
        raise NotImplementedError

    async def embed_query(self, text: str) -> list[float]:
        """Embed a query. See `Embedder.embed_query`."""
        raise NotImplementedError
