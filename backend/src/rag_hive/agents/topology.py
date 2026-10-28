"""Wire types of the agent map served at `GET /api/runs/{run_id}/graph`.

The nodes and edges themselves are declared in `rag_hive.agents.graph`, next to the LangGraph
workflow built from them. Nodes are agent roles, not instances: the `worker` node is a
template, and each worker the Planner spawns appears at runtime through events whose
`parent_instance_id` points at its spawner (see `rag_hive.events.schema.BaseEvent`).
"""

from typing import Literal

from rag_hive.core.wire import WireModel
from rag_hive.events.schema import AgentName

type EdgeKind = Literal["handoff", "fan_out", "fan_in"]
"""`handoff`: one agent passes control to the next. `fan_out` / `fan_in`: into and out of the
parallel workers."""


class GraphNode(WireModel):
    """One agent role on the map."""

    id: str
    agent: AgentName
    label: str
    dynamic: bool = False
    """True when the node stands for a variable number of runtime instances."""


class GraphEdge(WireModel):
    """A directed connection between two nodes."""

    id: str
    source: str
    target: str
    kind: EdgeKind


class RunGraph(WireModel):
    """Nodes and edges of a run's workflow."""

    run_id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
