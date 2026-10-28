"""Planner: picks the grid of pipeline configs to benchmark, from registered components only."""

from typing import TypedDict

from pydantic import Field, JsonValue

from rag_hive.agents.profiler import DocumentProfile
from rag_hive.core.data import DataModel


class PipelineConfig(DataModel):
    """One pipeline to benchmark: a registered component name and options per stage.

    Every name is a key of its registry (`parser_registry`...), and every options mapping is
    validated by that component's `config_model` when the Worker builds it.
    """

    id: str = Field(description="Unique within the run, e.g. `cfg-3`; workers report under it.")
    parser: str
    chunker: str
    embedder: str
    retriever: str
    parser_options: dict[str, JsonValue] = Field(default_factory=dict)
    chunker_options: dict[str, JsonValue] = Field(default_factory=dict)
    embedder_options: dict[str, JsonValue] = Field(default_factory=dict)
    retriever_options: dict[str, JsonValue] = Field(default_factory=dict)


class PlannerInput(DataModel):
    """What the Planner reads from the workflow state."""

    profile: DocumentProfile


class Plan(DataModel):
    """The configs to run and why they were chosen."""

    configs: list[PipelineConfig] = Field(min_length=1)
    rationale: str = Field(description="Why this grid fits the profile, for the dashboard.")


class PlannerUpdate(TypedDict):
    """State keys the Planner node writes."""

    plan: Plan


async def run_planner(inp: PlannerInput) -> Plan:
    """Choose pipeline configs suited to the profile (e.g. an OCR parser for scanned pages).

    Proposes only names registered in the component registries (AGENTS.md principle 1).
    """
    raise NotImplementedError


async def planner_node(state: PlannerInput) -> PlannerUpdate:
    """LangGraph node: plan the configs from the state's `profile` and store `plan`."""
    raise NotImplementedError
