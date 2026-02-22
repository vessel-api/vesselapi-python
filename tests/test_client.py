"""Tests for VesselClient and AsyncVesselClient construction and configuration."""

from __future__ import annotations

import httpx
import pytest
import respx

from vessel_api_python import AsyncVesselClient, VesselClient


class TestVesselClientConstruction:
    """Tests for sync client construction and validation."""

    def test_empty_api_key_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="api_key must not be empty"):
            VesselClient(api_key="")

    def test_valid_api_key_creates_client(self) -> None:
        client = VesselClient(api_key="test-key")
        assert client.vessels is not None
        assert client.ports is not None
        assert client.port_events is not None
        assert client.emissions is not None
        assert client.search is not None
        assert client.location is not None
        assert client.navtex is not None
        client.close()

    def test_default_base_url(self) -> None:
        client = VesselClient(api_key="test-key")
        assert "vesselapi.com" in str(client._client.base_url)
        client.close()

    def test_custom_base_url(self) -> None:
        client = VesselClient(api_key="test-key", base_url="https://custom.example.com/v2")
        assert "custom.example.com" in str(client._client.base_url)
        client.close()

    def test_custom_timeout(self) -> None:
        client = VesselClient(api_key="test-key", timeout=60.0)
        assert client._client.timeout.connect == 60.0
        client.close()

    def test_negative_max_retries_clamped_to_zero(self) -> None:
        # Should not raise — negative retries are clamped to 0.
        client = VesselClient(api_key="test-key", max_retries=-5)
        client.close()

    def test_context_manager(self) -> None:
        with VesselClient(api_key="test-key") as client:
            assert client.vessels is not None

    def test_auth_header_set(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessel/123").mock(
                return_value=httpx.Response(200, json={"vessel": {"imo": 123}})
            )
            client = VesselClient(api_key="my-secret-key", max_retries=0)
            client.vessels.get("123")
            assert route.called
            request = route.calls[0].request
            assert request.headers["Authorization"] == "Bearer my-secret-key"
            client.close()

    def test_user_agent_header_set(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessel/123").mock(
                return_value=httpx.Response(200, json={"vessel": {"imo": 123}})
            )
            client = VesselClient(api_key="key", user_agent="custom-agent/1.0", max_retries=0)
            client.vessels.get("123")
            request = route.calls[0].request
            assert request.headers["User-Agent"] == "custom-agent/1.0"
            client.close()


class TestAsyncVesselClientConstruction:
    """Tests for async client construction and validation."""

    def test_empty_api_key_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="api_key must not be empty"):
            AsyncVesselClient(api_key="")

    def test_valid_api_key_creates_client(self) -> None:
        client = AsyncVesselClient(api_key="test-key")
        assert client.vessels is not None
        assert client.ports is not None
        assert client.port_events is not None
        assert client.emissions is not None
        assert client.search is not None
        assert client.location is not None
        assert client.navtex is not None

    def test_negative_max_retries_clamped_to_zero(self) -> None:
        client = AsyncVesselClient(api_key="test-key", max_retries=-5)
        assert client is not None

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with AsyncVesselClient(api_key="test-key") as client:
            assert client.vessels is not None
