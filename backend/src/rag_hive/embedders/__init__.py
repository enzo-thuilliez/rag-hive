"""Embedders map text to dense vectors through a provider (see `Settings.embedding_provider`).

Implementations register with `@embedder_registry.register`. No implementation exists yet.
"""

from rag_hive.embedders.base import Embedder, EmbedderConfig, embedder_registry

__all__ = ["Embedder", "EmbedderConfig", "embedder_registry"]
