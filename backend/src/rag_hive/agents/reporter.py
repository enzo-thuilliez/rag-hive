"""Reporter: the last agent. Ranks the configs and writes the summary shown on the dashboard."""

from typing import TypedDict

from pydantic import Field

from rag_hive.agents.judge import ConfigScores, Scores
from rag_hive.agents.planner import PipelineConfig, Plan
from rag_hive.agents.profiler import DocumentProfile
from rag_hive.core.data import DataModel


class ReporterInput(DataModel):
    """What the Reporter reads from the workflow state."""

    run_id: str
    profile: DocumentProfile
    plan: Plan
    scores: Scores


class RankedConfig(DataModel):
    """One config's place in the ranking."""

    rank: int = Field(ge=1)
    config: PipelineConfig
    scores: ConfigScores


class Report(DataModel):
    """Final result of a run."""

    run_id: str
    primary_metric: str = Field(description="Metric the ranking sorts on, e.g. `recall@5`.")
    ranking: list[RankedConfig] = Field(description="Best first; failed configs last.")
    summary: str = Field(description="Short prose explanation of the result.")


class ReporterUpdate(TypedDict):
    """State keys the Reporter node writes."""

    report: Report


async def run_reporter(inp: ReporterInput) -> Report:
    """Rank configs by the primary metric and summarize why the best ones win.

    The ranking comes from the scores alone; the LLM only writes `summary`.
    """
    raise NotImplementedError


async def reporter_node(state: ReporterInput) -> ReporterUpdate:
    """LangGraph node: build the report and store `report`."""
    raise NotImplementedError
