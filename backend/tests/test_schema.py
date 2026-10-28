from datetime import UTC, datetime

from rag_hive.events.schema import AgentName, HandoffEvent, agent_event_adapter
from rag_hive.schema import SCHEMA_PATH, render_data_schemas, render_wire_schema


def test_event_round_trips_through_camel_case_json() -> None:
    event = HandoffEvent(
        run_id="run-1",
        seq=7,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        agent=AgentName.WORKER,
        agent_instance_id="worker-3",
        parent_instance_id="qa_generator",
        to_agent=AgentName.JUDGE,
    )

    raw = agent_event_adapter.dump_json(event)

    assert b'"parentInstanceId":"qa_generator"' in raw
    assert agent_event_adapter.validate_json(raw) == event


def test_committed_schema_is_up_to_date() -> None:
    assert SCHEMA_PATH.read_text(encoding="utf-8") == render_wire_schema(), (
        "frontend/src/api/schema.json is stale: run `make schema`"
    )


def test_committed_data_schemas_are_up_to_date() -> None:
    for path, content in render_data_schemas().items():
        stale = f"{path.name} is stale: run `make schema`"
        assert path.read_text(encoding="utf-8") == content, stale
