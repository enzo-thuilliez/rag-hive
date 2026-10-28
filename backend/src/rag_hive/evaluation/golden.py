"""Golden set: hand-reviewed questions with reference answers and the passages that answer them.

Expected passages are verbatim text spans with their page, not chunk ids, so the same golden set
scores every chunker (see `rag_hive.evaluation.span_matching`).
"""

from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from rag_hive.core.data import DataModel

type QuestionType = Literal[
    "factual", "table", "definition", "multi_hop", "procedural", "unanswerable"
]
"""What kind of reasoning a question needs. `unanswerable`: the document does not answer it."""

type Difficulty = Literal["easy", "medium", "hard"]
"""Reviewer's estimate of how hard the question is to retrieve and answer."""


class ExpectedPassage(DataModel):
    """A span of the document that (partly) answers a question."""

    page: int = Field(ge=1, description="1-based page the span starts on.")
    text: str = Field(min_length=1, description="The span, copied verbatim from the PDF.")


class GoldenQuestion(DataModel):
    """One reviewed question of the golden set."""

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", description="Stable kebab-case slug.")
    document_id: str = Field(description="`CorpusEntry.id` of the document the question is about.")
    question: str = Field(min_length=1)
    answer: str = Field(
        description="Reference answer. For `unanswerable`, why the document cannot answer it."
    )
    type: QuestionType
    difficulty: Difficulty
    expected_passages: list[ExpectedPassage] = Field(
        default_factory=list,
        description="Every span needed to answer. Empty if and only if `type` is unanswerable.",
    )

    @model_validator(mode="after")
    def _check_passages_match_type(self) -> Self:
        """Unanswerable questions have no passage, multi-hop ones at least two, others one."""
        count = len(self.expected_passages)
        if self.type == "unanswerable" and count:
            msg = f"{self.id}: an unanswerable question cannot have expected passages"
            raise ValueError(msg)
        minimum = {"unanswerable": 0, "multi_hop": 2}.get(self.type, 1)
        if count < minimum:
            msg = f"{self.id}: a {self.type} question needs at least {minimum} expected passage(s)"
            raise ValueError(msg)
        return self


def load_golden_set(path: Path) -> list[GoldenQuestion]:
    """Read and validate a golden set file.

    Args:
        path: A YAML file holding a list of questions.

    Returns:
        The questions in file order.

    Raises:
        FileNotFoundError: If `path` does not exist.
        pydantic.ValidationError: If a question does not match `GoldenQuestion`.
        ValueError: If two questions share an `id`.
    """
    raise NotImplementedError
