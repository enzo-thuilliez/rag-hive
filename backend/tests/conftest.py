"""Shared fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from rag_hive.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A test client on a fresh app, so dependency overrides don't leak between tests."""
    with TestClient(create_app()) as test_client:
        yield test_client
