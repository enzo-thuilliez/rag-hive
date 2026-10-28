"""Data passed between pipeline stages: parsed documents, chunks and retrieval hits.

Chunks keep their provenance (page, element type, parent, bounding box, parser) so the Judge
and the dashboard can trace every retrieved passage back to where it came from in the PDF.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, JsonValue

from rag_hive.core.wire import WireModel

type ElementType = Literal[
    "text", "heading", "list", "table", "image", "caption", "code", "formula"
]
"""Kind of document element a piece of text was extracted from."""


class BoundingBox(WireModel):
    """Rectangle on a page, in PDF points, origin at the top-left corner."""

    x0: float
    y0: float
    x1: float
    y1: float


class DocumentElement(WireModel):
    """One structural element extracted by a parser (a paragraph, a table, an image...)."""

    text: str
    page: int = Field(ge=1, description="1-based page number.")
    element_type: ElementType
    bbox: BoundingBox | None = None


class ParsedDocument(WireModel):
    """Output of a `Parser`: the document as an ordered list of elements."""

    source_path: Path
    parser: str = Field(description="Registry name of the parser that produced this document.")
    elements: list[DocumentElement]
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class Chunk(WireModel):
    """Output of a `Chunker`: a unit of text to embed and retrieve, with its provenance."""

    id: str
    text: str
    page: int = Field(ge=1, description="1-based page the chunk starts on.")
    element_type: ElementType
    parent_id: str | None = Field(
        default=None, description="Id of the enclosing chunk, for hierarchical chunking."
    )
    bbox: BoundingBox | None = None
    parser: str = Field(description="Registry name of the parser the text came from.")
    metadata: dict[str, JsonValue] = Field(default_factory=dict)


class ScoredChunk(WireModel):
    """Output of a `Retriever`: a chunk and its relevance score (higher is better)."""

    chunk: Chunk
    score: float
