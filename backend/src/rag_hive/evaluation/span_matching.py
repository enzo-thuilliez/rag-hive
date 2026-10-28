"""Match retrieved chunks to a question's expected passages, independently of the chunker.

Chunk ids change with every chunker, so relevance cannot be labelled per chunk. Instead the
golden set stores verbatim spans (`ExpectedPassage`), and a chunk counts as covering a span when
it contains enough of the span's normalized text on a nearby page. Every chunker is then scored
against the same labels.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from rag_hive.core.models import Chunk
from rag_hive.evaluation.golden import ExpectedPassage


@dataclass(frozen=True, slots=True)
class SpanMatch:
    """Which expected passages each retrieved chunk covers, in rank order.

    Attributes:
        expected_count: Number of expected passages of the question.
        covered: `covered[i]` holds the indices (into the expected passages) covered by the
            chunk at rank `i + 1`. Empty when the chunk covers none.
    """

    expected_count: int
    covered: tuple[frozenset[int], ...]


def normalize_text(text: str) -> str:
    """Normalize text for span comparison.

    Applies Unicode NFKC, lowercases, rejoins words hyphenated across line breaks, and collapses
    whitespace, so differences between parsers' text extraction do not count as mismatches.
    """
    raise NotImplementedError


def match_spans(
    chunks: Sequence[Chunk],
    expected: Sequence[ExpectedPassage],
    *,
    min_coverage: float = 0.5,
    page_tolerance: int = 1,
) -> SpanMatch:
    """Decide which expected passages each retrieved chunk covers.

    A chunk covers a passage when the passage's page is within `page_tolerance` of the chunk's
    page and at least `min_coverage` of the passage's normalized tokens appear in the chunk as
    one contiguous run (so a passage split across two chunks is covered by neither unless one
    holds enough of it).

    Args:
        chunks: Retrieved chunks, best first.
        expected: The question's expected passages.
        min_coverage: Fraction of a passage, in (0, 1], a chunk must contain to cover it.
        page_tolerance: How many pages a chunk's start page may differ from the passage's.

    Returns:
        The coverage of each chunk, in the order of `chunks`.

    Raises:
        ValueError: If `min_coverage` is not in (0, 1] or `page_tolerance` is negative.
    """
    raise NotImplementedError
