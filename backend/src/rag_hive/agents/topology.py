"""Static topology of the agent workflow, served to the dashboard's agent map.

Nodes are agent roles, not instances: the `worker` node is a template, and each worker the
Planner spawns appears at runtime through events whose `parent_instance_id` points at its
spawner (see `rag_hive.events.schema.BaseEvent`).
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


_NODES: tuple[GraphNode, ...] = (
    GraphNode(id=AgentName.PROFILER, agent=AgentName.PROFILER, label="Profiler"),
    GraphNode(id=AgentName.PLANNER, agent=AgentName.PLANNER, label="Planner"),
    GraphNode(id=AgentName.QA_GENERATOR, agent=AgentName.QA_GENERATOR, label="QA Generator"),
    GraphNode(id=AgentName.WORKER, agent=AgentName.WORKER, label="Workers", dynamic=True),
    GraphNode(id=AgentName.JUDGE, agent=AgentName.JUDGE, label="Judge"),
    GraphNode(id=AgentName.REPORTER, agent=AgentName.REPORTER, label="Reporter"),
)

_EDGES: tuple[tuple[AgentName, AgentName, EdgeKind], ...] = (
    (AgentName.PROFILER, AgentName.PLANNER, "handoff"),
    (AgentName.PLANNER, AgentName.QA_GENERATOR, "handoff"),
    (AgentName.QA_GENERATOR, AgentName.WORKER, "fan_out"),
    (AgentName.WORKER, AgentName.JUDGE, "fan_in"),
    (AgentName.JUDGE, AgentName.REPORTER, "handoff"),
)


def build_run_graph(run_id: str) -> RunGraph:
    """Return the workflow graph for `run_id`. The same for every run until the Planner exists."""
    return RunGraph(
        run_id=run_id,
        nodes=list(_NODES),
        edges=[
            GraphEdge(id=f"{source}->{target}", source=source, target=target, kind=kind)
            for source, target, kind in _EDGES
        ],
    )
