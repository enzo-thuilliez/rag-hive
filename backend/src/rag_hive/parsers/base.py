"""Parser interface and registry."""

from abc import abstractmethod
from pathlib import Path

from rag_hive.core.component import Component, ComponentConfig
from rag_hive.core.models import ParsedDocument
from rag_hive.core.registry import Registry


class ParserConfig(ComponentConfig):
    """Options shared by every parser. Subclass per parser."""


class Parser(Component):
    """Extracts structured elements from a document file."""

    @abstractmethod
    async def parse(self, path: Path) -> ParsedDocument:
        """Parse the file at `path`.

        Args:
            path: Local path of the PDF to parse.

        Returns:
            The document's elements in reading order, with `parser` set to this `name`.
        """


parser_registry: Registry[Parser] = Registry("parser")
"""Every registered parser, by name."""
