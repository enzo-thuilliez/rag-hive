"""Chunker interface and registry."""

from abc import abstractmethod

from rag_hive.core.component import Component, ComponentConfig
from rag_hive.core.models import Chunk, ParsedDocument
from rag_hive.core.registry import Registry


class ChunkerConfig(ComponentConfig):
    """Options shared by every chunker. Subclass per chunker."""


class Chunker(Component):
    """Splits a parsed document into retrievable chunks."""

    @abstractmethod
    async def chunk(self, document: ParsedDocument) -> list[Chunk]:
        """Split `document` into chunks.

        Args:
            document: Output of a `Parser`.

        Returns:
            Chunks in document order. Each one carries the page, element type, bbox and parser
            of its source elements, and `parent_id` when the strategy is hierarchical.
        """


chunker_registry: Registry[Chunker] = Registry("chunker")
"""Every registered chunker, by name."""
