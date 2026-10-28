"""Every backend route lives under /api (ADR-004), so the frontend owns all other paths.

`app.routes` keeps an included router as one opaque node, so this checks the OpenAPI schema
(every API route, however routers nest), the top-level routes left out of the schema (docs),
and that the old root paths no longer answer.
"""

import pytest
from fastapi.testclient import TestClient

from rag_hive.api import API_PREFIX
from rag_hive.main import create_app


def test_every_openapi_path_is_under_the_prefix() -> None:
    paths = list(create_app().openapi()["paths"])

    assert {
        f"{API_PREFIX}/health",
        f"{API_PREFIX}/runs/{{run_id}}/events",
        f"{API_PREFIX}/runs/{{run_id}}/graph",
    } <= set(paths)
    assert [path for path in paths if not path.startswith(f"{API_PREFIX}/")] == []


def test_every_top_level_route_is_under_the_prefix() -> None:
    paths = [getattr(route, "path", None) for route in create_app().routes]

    outside = [path for path in paths if path is not None and not path.startswith(f"{API_PREFIX}/")]
    assert outside == []


@pytest.mark.parametrize(
    "path",
    [
        "/health",
        "/runs/run-1/events",
        "/runs/run-1/graph",
        "/docs",
        "/docs/oauth2-redirect",
        "/openapi.json",
        "/redoc",
    ],
)
def test_root_paths_are_not_served(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 404
