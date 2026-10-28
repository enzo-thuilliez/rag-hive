from fastapi.testclient import TestClient

from rag_hive.agents.topology import RunGraph
from rag_hive.events.schema import AgentName


def test_graph_covers_every_agent_once(client: TestClient) -> None:
    response = client.get("/runs/run-1/graph")

    assert response.status_code == 200
    graph = RunGraph.model_validate(response.json())
    assert graph.run_id == "run-1"
    assert sorted(node.agent for node in graph.nodes) == sorted(AgentName)


def test_graph_edges_reference_existing_nodes(client: TestClient) -> None:
    graph = RunGraph.model_validate(client.get("/runs/run-1/graph").json())

    node_ids = {node.id for node in graph.nodes}
    for edge in graph.edges:
        assert edge.source in node_ids
        assert edge.target in node_ids


def test_only_workers_are_dynamic(client: TestClient) -> None:
    graph = RunGraph.model_validate(client.get("/runs/run-1/graph").json())

    assert [node.agent for node in graph.nodes if node.dynamic] == [AgentName.WORKER]


def test_graph_json_is_camel_case(client: TestClient) -> None:
    body = client.get("/runs/run-1/graph").json()

    assert "runId" in body
