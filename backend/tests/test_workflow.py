from typing import get_args

from rag_hive.agents.graph import WORKFLOW_EDGES, WORKFLOW_NODES, build_workflow
from rag_hive.config import EmbeddingProviderName, LLMProviderName
from rag_hive.embedders import embedder_registry
from rag_hive.events.schema import AgentName
from rag_hive.llm import llm_registry


def test_workflow_compiles_with_one_node_per_agent() -> None:
    drawable = build_workflow().compile().get_graph()

    assert set(drawable.nodes) - {"__start__", "__end__"} == {str(agent) for agent in AgentName}
    assert [node.agent for node in WORKFLOW_NODES] == list(AgentName)


def test_langgraph_edges_are_the_declared_topology() -> None:
    drawable = build_workflow().compile().get_graph()

    edges = {(edge.source, edge.target, edge.conditional) for edge in drawable.edges}
    declared = {
        (str(source), str(target), kind == "fan_out") for source, target, kind in WORKFLOW_EDGES
    }
    first, last = str(WORKFLOW_NODES[0].agent), str(WORKFLOW_NODES[-1].agent)
    assert edges == declared | {("__start__", first, False), (last, "__end__", False)}


def test_every_configurable_provider_is_registered() -> None:
    assert set(get_args(LLMProviderName.__value__)) <= set(llm_registry.names())
    assert set(get_args(EmbeddingProviderName.__value__)) <= set(embedder_registry.names())
