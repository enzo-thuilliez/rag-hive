"""Run endpoints: the live event stream and the workflow graph."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from rag_hive.agents.topology import RunGraph, build_run_graph
from rag_hive.events.source import RunEventSource, get_event_source
from rag_hive.events.sse import format_sse

router = APIRouter(prefix="/runs", tags=["runs"])


def parse_last_event_id(
    last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
) -> int | None:
    """Read the SSE `Last-Event-ID` header as the last `seq` the client received.

    Raises:
        HTTPException: 400 if the header is present but not a non-negative integer.
    """
    if last_event_id is None:
        return None
    try:
        seq = int(last_event_id)
    except ValueError:
        seq = -1
    if seq < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last-Event-ID must be a non-negative integer event seq",
        )
    return seq


@router.get(
    "/{run_id}/events",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/event-stream": {}}}},
)
async def stream_run_events(
    run_id: str,
    after_seq: Annotated[int | None, Depends(parse_last_event_id)],
    source: Annotated[RunEventSource, Depends(get_event_source)],
) -> StreamingResponse:
    """Stream the run's agent events as SSE, resuming after `Last-Event-ID` when sent."""

    async def frames() -> AsyncIterator[str]:
        async for event in source.stream(run_id, after_seq):
            if after_seq is not None and event.seq <= after_seq:
                continue
            yield format_sse(event)

    return StreamingResponse(
        frames(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{run_id}/graph")
async def get_run_graph(run_id: str) -> RunGraph:
    """Return the nodes and edges of the run's agent workflow."""
    return build_run_graph(run_id)
