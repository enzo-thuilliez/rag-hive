"""Embedder interface and registry."""

from abc import abstractmethod
from collections.abc import Sequence

from rag_hive.core.component import Component, ComponentConfig
from rag_hive.core.registry import Registry


class EmbedderConfig(ComponentConfig):
    """Options shared by every embedder. Subclass per embedder."""


class Embedder(Component):
    """Turns text into fixed-size vectors."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Length of the vectors this embedder returns."""

    @abstractmethod
    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed passages to be indexed.

        Args:
            texts: Passages, typically `Chunk.text`.

        Returns:
            One vector of length `dimension` per input, in input order.
        """

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Embed a search query (some models embed queries and passages differently).

        Args:
            text: The query.

        Returns:
            A vector of length `dimension`.
        """


embedder_registry: Registry[Embedder] = Registry("embedder")
"""Every registered embedder, by name."""
