"""Where the SSE endpoint reads a run's events from."""

from collections.abc import AsyncIterator
from typing import Protocol

from rag_hive.events.schema import AgentEvent


class RunEventSource(Protocol):
    """Supplies a run's events, past and live."""

    def stream(self, run_id: str, after_seq: int | None) -> AsyncIterator[AgentEvent]:
        """Yield the events of `run_id` in `seq` order.

        Args:
            run_id: The run to stream.
            after_seq: When resuming, the last `seq` the client received. Sources should skip
                events up to and including it; the endpoint filters them out regardless.
        """
        ...


class EmptyEventSource:
    """Placeholder source with no events, until the agent workflow publishes some."""

    async def stream(self, run_id: str, after_seq: int | None) -> AsyncIterator[AgentEvent]:
        """Yield nothing, so the stream closes right away."""
        del run_id, after_seq
        events: list[AgentEvent] = []
        for event in events:
            yield event


def get_event_source() -> RunEventSource:
    """FastAPI dependency returning the active event source. Overridden in tests."""
    return EmptyEventSource()
