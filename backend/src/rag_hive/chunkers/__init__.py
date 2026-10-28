"""Chunkers split a `ParsedDocument` into `Chunk`s that keep their provenance.

Async, because semantic and agentic chunkers call models. Implementations register with
`@chunker_registry.register`. No implementation exists yet.
"""

from rag_hive.chunkers.base import Chunker, ChunkerConfig, chunker_registry

__all__ = ["Chunker", "ChunkerConfig", "chunker_registry"]
