"""Shared test fixtures for Vessel API Python SDK tests."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
import respx

from vessel_api_python import VesselClient


@pytest.fixture()
def mock_api():
    """Return a respx mock router for intercepting HTTP requests."""
    with respx.mock() as router:
        yield router


@pytest.fixture()
def client(mock_api: respx.MockRouter) -> VesselClient:
    """Return a VesselClient configured to use the mock API."""
    return VesselClient(api_key="test-api-key", max_retries=0)


def json_response(data: Any, status_code: int = 200) -> httpx.Response:
    """Create a mock httpx.Response with JSON body."""
    return httpx.Response(
        status_code=status_code,
        content=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
