"""Parsers turn a PDF into a `ParsedDocument` (ordered elements with page and bbox).

Implementations live in this package, one module each, and register with
`@parser_registry.register`. No implementation exists yet.
"""

from rag_hive.parsers.base import Parser, ParserConfig, parser_registry

__all__ = ["Parser", "ParserConfig", "parser_registry"]
