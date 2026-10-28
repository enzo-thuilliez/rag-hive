"""Server-Sent Events framing."""

from rag_hive.events.schema import AgentEvent, agent_event_adapter


def format_sse(event: AgentEvent) -> str:
    """Render `event` as one SSE frame.

    The frame's `id` is the event's `seq`, so a reconnecting `EventSource` sends it back as
    `Last-Event-ID` and the stream resumes after it. The SSE `event` name is the event `type`.
    """
    data = agent_event_adapter.dump_json(event).decode()
    return f"id: {event.seq}\nevent: {event.type}\ndata: {data}\n\n"
