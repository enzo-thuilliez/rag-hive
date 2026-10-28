"""Liveness endpoint."""

from typing import Literal

from fastapi import APIRouter

from rag_hive import __version__
from rag_hive.core.wire import WireModel

router = APIRouter(tags=["health"])


class HealthResponse(WireModel):
    """Body of `GET /health`."""

    status: Literal["ok"]
    version: str


@router.get("/health")
async def get_health() -> HealthResponse:
    """Report that the backend is up, with its version."""
    return HealthResponse(status="ok", version=__version__)
