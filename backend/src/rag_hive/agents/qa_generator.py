"""QA Generator: the questions every worker answers, from the golden set or generated."""

from pathlib import Path
from typing import Literal, TypedDict

from pydantic import Field

from rag_hive.agents.profiler import DocumentProfile
from rag_hive.core.data import DataModel
from rag_hive.evaluation.golden import GoldenQuestion

type QuestionSource = Literal["golden", "generated", "mixed"]
"""Where a question set comes from: the reviewed golden set, the LLM, or both."""


class QAGeneratorInput(DataModel):
    """What the QA Generator reads from the workflow state."""

    document_id: str
    pdf_path: Path
    profile: DocumentProfile
    golden_set: list[GoldenQuestion] = Field(
        description="Reviewed questions for this document; empty when there are none."
    )


class QuestionSet(DataModel):
    """The questions of a run, in the golden-set format so the Judge scores them alike."""

    questions: list[GoldenQuestion] = Field(min_length=1)
    source: QuestionSource


class QAGeneratorUpdate(TypedDict):
    """State keys the QA Generator node writes."""

    question_set: QuestionSet


async def run_qa_generator(inp: QAGeneratorInput) -> QuestionSet:
    """Return the run's questions.

    Uses the golden set when the document has one. Otherwise asks the LLM for questions with
    verbatim expected passages, and drops any whose passage text is not found in the PDF.
    """
    raise NotImplementedError


async def qa_generator_node(state: QAGeneratorInput) -> QAGeneratorUpdate:
    """LangGraph node: build the question set and store `question_set`."""
    raise NotImplementedError
