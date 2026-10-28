"""The workflow topology, declared once and used for both LangGraph and the dashboard.

`WORKFLOW_NODES` and `WORKFLOW_EDGES` are the single declaration. `build_workflow` wires the
LangGraph `StateGraph` from them, and `build_run_graph` serves the same nodes and edges at
`GET /api/runs/{run_id}/graph`, so the agent map cannot drift from the graph that runs.

    Profiler → Planner → QA Generator → Workers (one per config, in parallel) → Judge → Reporter
"""

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from rag_hive.agents.judge import JudgeInput, judge_node
from rag_hive.agents.planner import PlannerInput, planner_node
from rag_hive.agents.profiler import ProfilerInput, profiler_node
from rag_hive.agents.qa_generator import QAGeneratorInput, qa_generator_node
from rag_hive.agents.reporter import ReporterInput, reporter_node
from rag_hive.agents.state import WorkflowState
from rag_hive.agents.topology import EdgeKind, GraphEdge, GraphNode, RunGraph
from rag_hive.agents.worker import WorkerInput, worker_node
from rag_hive.events.schema import AgentName

WORKFLOW_NODES: tuple[GraphNode, ...] = (
    GraphNode(id=AgentName.PROFILER, agent=AgentName.PROFILER, label="Profiler"),
    GraphNode(id=AgentName.PLANNER, agent=AgentName.PLANNER, label="Planner"),
    GraphNode(id=AgentName.QA_GENERATOR, agent=AgentName.QA_GENERATOR, label="QA Generator"),
    GraphNode(id=AgentName.WORKER, agent=AgentName.WORKER, label="Workers", dynamic=True),
    GraphNode(id=AgentName.JUDGE, agent=AgentName.JUDGE, label="Judge"),
    GraphNode(id=AgentName.REPORTER, agent=AgentName.REPORTER, label="Reporter"),
)
"""Agent roles, in workflow order. Node ids are the LangGraph node names."""

WORKFLOW_EDGES: tuple[tuple[AgentName, AgentName, EdgeKind], ...] = (
    (AgentName.PROFILER, AgentName.PLANNER, "handoff"),
    (AgentName.PLANNER, AgentName.QA_GENERATOR, "handoff"),
    (AgentName.QA_GENERATOR, AgentName.WORKER, "fan_out"),
    (AgentName.WORKER, AgentName.JUDGE, "fan_in"),
    (AgentName.JUDGE, AgentName.REPORTER, "handoff"),
)
"""Directed edges `(source, target, kind)`. Runs start at the first node, end after the last."""


def fan_out_workers(state: WorkflowState) -> list[Send]:
    """Conditional edge after the QA Generator: one `Send` to the worker node per config.

    Each `Send` carries a `WorkerInput` with the config, the PDF, the question set's questions
    and `top_k = max(state.ks)`, and a worker id `worker-<n>` (1-based, in plan order).
    """
    raise NotImplementedError


def build_workflow() -> StateGraph[WorkflowState, None, WorkflowState, WorkflowState]:
    """Return the uncompiled LangGraph workflow, wired from `WORKFLOW_EDGES`.

    Each node receives only its input model (LangGraph `input_schema`) and returns the state
    keys it writes. `handoff` and `fan_in` edges are plain edges; the `fan_out` edge is
    `fan_out_workers`, and LangGraph waits for every worker before running the fan-in target.
    """
    graph = StateGraph(WorkflowState)
    graph.add_node(AgentName.PROFILER.value, profiler_node, input_schema=ProfilerInput)
    graph.add_node(AgentName.PLANNER.value, planner_node, input_schema=PlannerInput)
    graph.add_node(AgentName.QA_GENERATOR.value, qa_generator_node, input_schema=QAGeneratorInput)
    graph.add_node(AgentName.WORKER.value, worker_node, input_schema=WorkerInput)
    graph.add_node(AgentName.JUDGE.value, judge_node, input_schema=JudgeInput)
    graph.add_node(AgentName.REPORTER.value, reporter_node, input_schema=ReporterInput)

    graph.add_edge(START, WORKFLOW_NODES[0].agent.value)
    for source, target, kind in WORKFLOW_EDGES:
        if kind == "fan_out":
            graph.add_conditional_edges(source.value, fan_out_workers, [target.value])
        else:
            graph.add_edge(source.value, target.value)
    graph.add_edge(WORKFLOW_NODES[-1].agent.value, END)
    return graph


def build_run_graph(run_id: str) -> RunGraph:
    """Return the workflow graph for `run_id`. The same for every run until the Planner exists."""
    return RunGraph(
        run_id=run_id,
        nodes=list(WORKFLOW_NODES),
        edges=[
            GraphEdge(id=f"{source}->{target}", source=source, target=target, kind=kind)
            for source, target, kind in WORKFLOW_EDGES
        ],
    )
