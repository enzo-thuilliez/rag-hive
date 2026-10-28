"""HTTP routes. Every backend route lives under `API_PREFIX`; the frontend owns all other paths.

See ADR-004 in DECISIONS.md.
"""

from fastapi import APIRouter

from rag_hive.api import health, runs

API_PREFIX = "/api"
"""Path prefix shared by every backend route, including the OpenAPI docs."""

router = APIRouter(prefix=API_PREFIX)
router.include_router(health.router)
router.include_router(runs.router)
