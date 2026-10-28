"""Embedders map text to dense vectors. `Settings.embedding_provider` names the default one.

Implementations register with `@embedder_registry.register`; importing this package registers
them all. The only one is the local sentence-transformers embedder (BGE-M3 by default,
ADR-005), and it is a stub.
"""

from rag_hive.embedders.base import Embedder, EmbedderConfig, embedder_registry
from rag_hive.embedders.sentence_transformer import (
    SentenceTransformerConfig,
    SentenceTransformerEmbedder,
)

__all__ = [
    "Embedder",
    "EmbedderConfig",
    "SentenceTransformerConfig",
    "SentenceTransformerEmbedder",
    "embedder_registry",
]
