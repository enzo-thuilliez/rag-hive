"""Judge: scores every worker's retrievals against the question set with evaluation code."""

from typing import TypedDict

from pydantic import Field

from rag_hive.agents.qa_generator import QuestionSet
from rag_hive.agents.worker import WorkerOutput
from rag_hive.core.data import DataModel
from rag_hive.evaluation.metrics.retrieval import RetrievalScores


class JudgeInput(DataModel):
    """What the Judge reads from the workflow state."""

    question_set: QuestionSet
    worker_outputs: list[WorkerOutput]
    ks: list[int] = Field(min_length=1)


class ConfigScores(DataModel):
    """Scores of one config."""

    config_id: str
    retrieval: RetrievalScores | None = Field(
        default=None, description="None when the worker failed or no question is answerable."
    )
    error: str | None = Field(default=None, description="The worker's error, passed through.")


class Scores(DataModel):
    """Scores of every config of the run."""

    configs: list[ConfigScores]


class JudgeUpdate(TypedDict):
    """State keys the Judge node writes."""

    scores: Scores


async def run_judge(inp: JudgeInput) -> Scores:
    """Score each worker output.

    Matches each question's hits to its expected passages
    (`rag_hive.evaluation.span_matching.match_spans`), then averages the retrieval metrics
    (`rag_hive.evaluation.metrics.retrieval.score_retrieval`). Every number comes from those
    functions, never from LLM text (AGENTS.md principle 2).
    """
    raise NotImplementedError


async def judge_node(state: JudgeInput) -> JudgeUpdate:
    """LangGraph node: score all worker outputs and store `scores`."""
    raise NotImplementedError
