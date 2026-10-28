"""Retrieval metrics over `SpanMatch` results: recall@k, hit rate@k, MRR and nDCG@k.

Every per-question metric takes the `SpanMatch` of one question and returns a value in [0, 1].
Unanswerable questions have no expected passage, so these metrics are undefined for them: the
functions raise `ValueError` and the Judge scores those questions separately.
"""

from collections.abc import Sequence

from pydantic import Field

from rag_hive.core.data import DataModel
from rag_hive.evaluation.span_matching import SpanMatch


class RetrievalScores(DataModel):
    """Retrieval metrics of one pipeline config, averaged over the answerable questions."""

    question_count: int = Field(ge=0, description="Answerable questions averaged over.")
    recall_at_k: dict[int, float]
    hit_rate_at_k: dict[int, float]
    ndcg_at_k: dict[int, float]
    mrr: float = Field(ge=0, le=1)


def recall_at_k(match: SpanMatch, k: int) -> float:
    """Fraction of the expected passages covered by at least one of the top `k` chunks.

    Raises:
        ValueError: If `k < 1` or the question has no expected passage.
    """
    raise NotImplementedError


def hit_rate_at_k(match: SpanMatch, k: int) -> float:
    """1.0 if any of the top `k` chunks covers an expected passage, else 0.0.

    Averaged over questions, this is the hit rate.

    Raises:
        ValueError: If `k < 1` or the question has no expected passage.
    """
    raise NotImplementedError


def reciprocal_rank(match: SpanMatch) -> float:
    """1 / rank of the first chunk that covers an expected passage, or 0.0 if none does.

    Raises:
        ValueError: If the question has no expected passage.
    """
    raise NotImplementedError


def mean_reciprocal_rank(matches: Sequence[SpanMatch]) -> float:
    """Mean of `reciprocal_rank` over questions (MRR).

    Raises:
        ValueError: If `matches` is empty or a question has no expected passage.
    """
    raise NotImplementedError


def ndcg_at_k(match: SpanMatch, k: int) -> float:
    """Normalized discounted cumulative gain of the top `k` chunks, with binary gains.

    A chunk gains 1 when it covers an expected passage that no higher-ranked chunk covered, so
    near-duplicate chunks are not rewarded twice. The ideal ranking covers one new passage per
    rank, for `min(k, expected_count)` ranks.

    Raises:
        ValueError: If `k < 1` or the question has no expected passage.
    """
    raise NotImplementedError


def score_retrieval(matches: Sequence[SpanMatch], ks: Sequence[int]) -> RetrievalScores:
    """Average every metric over `matches` (answerable questions only), at each `k` in `ks`.

    Raises:
        ValueError: If `matches` or `ks` is empty, or a question has no expected passage.
    """
    raise NotImplementedError
