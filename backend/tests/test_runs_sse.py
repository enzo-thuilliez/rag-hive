from collections.abc import AsyncIterator
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from rag_hive.events.schema import AgentEvent, AgentName, ProgressEvent, agent_event_adapter
from rag_hive.events.source import get_event_source


class FakeEventSource:
    """Replays fixed events and records how it was called."""

    def __init__(self, events: list[AgentEvent]) -> None:
        self.events = events
        self.calls: list[tuple[str, int | None]] = []

    async def stream(self, run_id: str, after_seq: int | None) -> AsyncIterator[AgentEvent]:
        self.calls.append((run_id, after_seq))
        for event in self.events:
            yield event


def make_events(count: int) -> list[AgentEvent]:
    return [
        ProgressEvent(
            run_id="run-1",
            seq=seq,
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            agent=AgentName.PROFILER,
            message=f"step {seq}",
        )
        for seq in range(1, count + 1)
    ]


def parse_frames(body: str) -> list[dict[str, str]]:
    frames = []
    for raw in body.split("\n\n"):
        if not raw.strip():
            continue
        fields = dict(line.split(": ", 1) for line in raw.splitlines())
        frames.append(fields)
    return frames


def use_source(client: TestClient, source: FakeEventSource) -> None:
    client.app.dependency_overrides[get_event_source] = lambda: source  # type: ignore[attr-defined]


def test_default_source_streams_nothing(client: TestClient) -> None:
    response = client.get("/api/runs/run-1/events")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.text == ""


def test_frames_carry_seq_as_id_and_type_as_event(client: TestClient) -> None:
    source = FakeEventSource(make_events(2))
    use_source(client, source)

    frames = parse_frames(client.get("/api/runs/run-1/events").text)

    assert [frame["id"] for frame in frames] == ["1", "2"]
    assert {frame["event"] for frame in frames} == {"progress"}
    first = agent_event_adapter.validate_json(frames[0]["data"])
    assert first == source.events[0]
    assert source.calls == [("run-1", None)]


def test_last_event_id_resumes_after_that_seq(client: TestClient) -> None:
    source = FakeEventSource(make_events(4))
    use_source(client, source)

    response = client.get("/api/runs/run-1/events", headers={"Last-Event-ID": "2"})

    assert source.calls == [("run-1", 2)]
    assert [frame["id"] for frame in parse_frames(response.text)] == ["3", "4"]


def test_invalid_last_event_id_is_rejected(client: TestClient) -> None:
    for bad in ("abc", "-1"):
        response = client.get("/api/runs/run-1/events", headers={"Last-Event-ID": bad})
        assert response.status_code == 400
