"""Agent events streamed to the frontend over SSE.

Every event shares the `BaseEvent` envelope and adds a `type` discriminator plus a payload.
The TypeScript mirror lives in `frontend/src/api/events.ts` and is checked against the JSON
Schema that `python -m rag_hive.schema` exports; change both in the same commit.
"""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, JsonValue, TypeAdapter

from rag_hive.core.wire import WireModel


class AgentName(StrEnum):
    """Agent roles in the workflow."""

    PROFILER = "profiler"
    PLANNER = "planner"
    QA_GENERATOR = "qa_generator"
    WORKER = "worker"
    JUDGE = "judge"
    REPORTER = "reporter"


class BaseEvent(WireModel):
    """Envelope shared by every event."""

    run_id: str
    seq: int = Field(ge=0, description="Per-run sequence number, strictly increasing. SSE `id`.")
    timestamp: AwareDatetime
    agent: AgentName
    agent_instance_id: str | None = Field(
        default=None, description="Distinguishes instances of a role, e.g. `worker-3`."
    )
    parent_instance_id: str | None = Field(
        default=None,
        description="Instance (or role, for singletons) that spawned this agent; attaches "
        "dynamic workers to their spawner on the agent map.",
    )


class AgentStartedEvent(BaseEvent):
    """An agent began working."""

    type: Literal["agent_started"] = "agent_started"
    task: str = Field(description="What the agent is about to do, for display.")


class ToolCallEvent(BaseEvent):
    """An agent called a tool."""

    type: Literal["tool_call"] = "tool_call"
    tool: str
    arguments: dict[str, JsonValue] = Field(default_factory=dict)


class ProgressEvent(BaseEvent):
    """Intermediate progress of a long step."""

    type: Literal["progress"] = "progress"
    message: str
    fraction: float | None = Field(default=None, ge=0, le=1)


class ResultEvent(BaseEvent):
    """An agent produced its output."""

    type: Literal["result"] = "result"
    summary: str
    data: dict[str, JsonValue] = Field(default_factory=dict)


class HandoffEvent(BaseEvent):
    """An agent passed control to another."""

    type: Literal["handoff"] = "handoff"
    to_agent: AgentName
    to_instance_id: str | None = None
    reason: str = ""


class ErrorEvent(BaseEvent):
    """An agent failed."""

    type: Literal["error"] = "error"
    message: str
    recoverable: bool = False


type AgentEvent = Annotated[
    AgentStartedEvent | ToolCallEvent | ProgressEvent | ResultEvent | HandoffEvent | ErrorEvent,
    Field(discriminator="type"),
]
"""Any agent event, discriminated by `type`."""

agent_event_adapter: TypeAdapter[AgentEvent] = TypeAdapter(AgentEvent)
"""Validates and serializes `AgentEvent` values (a union has no `model_validate` of its own)."""
