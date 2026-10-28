"""Parsing quality metrics: text fidelity (edit distance) and table structure (TEDS).

Both compare a parser's output to a reference transcription of the same page or table.
"""


def normalized_edit_distance(predicted: str, reference: str) -> float:
    """Levenshtein distance between the two texts, divided by the longer one's length.

    Texts are compared after `rag_hive.evaluation.span_matching.normalize_text`.

    Returns:
        A value in [0, 1]; 0 means identical. Two empty texts score 0.
    """
    raise NotImplementedError


def teds(predicted_html: str, reference_html: str, *, structure_only: bool = False) -> float:
    """Tree-Edit-Distance-based Similarity between two tables written as HTML.

    `1 - tree_edit_distance / max(node_count)`, as defined for PubTabNet (Zhong et al., 2020).

    Args:
        predicted_html: The parser's table as an HTML `<table>`.
        reference_html: The reference table as an HTML `<table>`.
        structure_only: Ignore cell text and compare the row, column and span structure only
            (TEDS-S).

    Returns:
        A value in [0, 1]; 1 means identical.

    Raises:
        ValueError: If either input does not contain a `<table>` element.
    """
    raise NotImplementedError
