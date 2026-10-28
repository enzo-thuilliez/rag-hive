"""Retriever interface and registry."""

from abc import abstractmethod
from collections.abc import Sequence

from rag_hive.core.component import Component, ComponentConfig
from rag_hive.core.models import Chunk, ScoredChunk
from rag_hive.core.registry import Registry


class RetrieverConfig(ComponentConfig):
    """Options shared by every retriever. Subclass per retriever."""


class Retriever(Component):
    """Indexes chunks, then answers top-k queries over them."""

    @abstractmethod
    async def index(self, chunks: Sequence[Chunk]) -> None:
        """Add `chunks` to the index."""

    @abstractmethod
    async def search(self, query: str, k: int) -> list[ScoredChunk]:
        """Return up to `k` chunks for `query`, best first.

        Args:
            query: Natural-language question.
            k: Maximum number of results.
        """


retriever_registry: Registry[Retriever] = Registry("retriever")
"""Every registered retriever, by name."""
