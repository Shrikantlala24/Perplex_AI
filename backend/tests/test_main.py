"""
Integration tests for main.py auth wiring.
We mock verify_clerk_token via FastAPI dependency_overrides to isolate route
behaviour from auth logic. We also mock get_query_list + web_search +
stream_synthesis so we don't hit real APIs.
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app
from auth import verify_clerk_token


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _fake_stream():
    """Async generator that yields one chunk — simulates stream_synthesis."""
    yield "Hello from the synthesizer."


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """TestClient with auth dependency overridden and all external calls mocked."""
    # Use FastAPI's dependency_overrides so the Depends() wiring is bypassed
    # correctly — patch("main.verify_clerk_token") won't work because Depends()
    # captures the function reference at decoration time, not by name lookup.
    app.dependency_overrides[verify_clerk_token] = lambda: "user_test_123"

    with patch("main.get_query_list", return_value=["test query"]), \
         patch("main.web_search", return_value=[{"results": []}]), \
         patch("main.stream_synthesis", return_value=_fake_stream()):
        yield TestClient(app)

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_query_with_valid_auth_returns_200(client):
    """A request with a (mocked) valid token should succeed."""
    response = client.post(
        "/query",
        json={"query": "What is LangChain?"},
        headers={"Authorization": "Bearer fake_token"},
    )
    assert response.status_code == 200


def test_query_without_auth_returns_403():
    """A request with no Authorization header should be rejected before auth."""
    # Don't override verify_clerk_token here — we want the real HTTPBearer to fire.
    with patch("main.get_query_list", return_value=[]), \
         patch("main.web_search", return_value=[]):
        unauthenticated_client = TestClient(app, raise_server_exceptions=False)
        response = unauthenticated_client.post(
            "/query",
            json={"query": "test"},
            # No Authorization header
        )
    # HTTPBearer with auto_error=True returns 403 when header is missing.
    assert response.status_code == 403


def test_health_endpoint_needs_no_auth():
    """/health must work without any Authorization header."""
    c = TestClient(app)
    response = c.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
