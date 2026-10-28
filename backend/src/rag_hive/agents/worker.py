"""Worker: runs one pipeline config end to end. The Planner's grid fans out to one per config."""

from pathlib import Path
from typing import TypedDict

from pydantic import Field

from rag_hive.agents.planner import PipelineConfig
from rag_hive.core.data import DataModel
from rag_hive.core.models import ScoredChunk
from rag_hive.evaluation.golden import GoldenQuestion


class WorkerInput(DataModel):
    """One worker's task, sent to it with LangGraph's `Send` rather than read from the state."""

    run_id: str
    worker_id: str = Field(description="Instance id in events, e.g. `worker-3`.")
    config: PipelineConfig
    pdf_path: Path
    questions: list[GoldenQuestion]
    top_k: int = Field(ge=1, description="Chunks to retrieve per question: the largest k scored.")


class QuestionRetrieval(DataModel):
    """What the pipeline retrieved for one question."""

    question_id: str
    hits: list[ScoredChunk] = Field(description="Best first, at most `top_k`.")
    latency_ms: float = Field(ge=0)


class WorkerOutput(DataModel):
    """Everything one config produced, or why it failed."""

    config_id: str
    worker_id: str
    retrievals: list[QuestionRetrieval] = Field(default_factory=list)
    chunk_count: int = Field(default=0, ge=0)
    parse_seconds: float = Field(default=0, ge=0)
    index_seconds: float = Field(default=0, ge=0)
    error: str | None = Field(
        default=None, description="Set when the pipeline failed; other workers carry on."
    )


class WorkerUpdate(TypedDict):
    """State keys the Worker node writes. `worker_outputs` is appended to, not replaced."""

    worker_outputs: list[WorkerOutput]


async def run_worker(inp: WorkerInput) -> WorkerOutput:
    """Parse, chunk, embed, index, then retrieve `top_k` chunks for every question.

    Builds each component with `registry.create(name, options)`. A failure is caught, emitted
    as an `error` event and returned in `WorkerOutput.error` (AGENTS.md principle 5).
    """
    raise NotImplementedError


async def worker_node(state: WorkerInput) -> WorkerUpdate:
    """LangGraph node: run one config and append its output to `worker_outputs`."""
    raise NotImplementedError
