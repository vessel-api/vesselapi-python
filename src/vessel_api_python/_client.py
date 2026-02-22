"""High-level Vessel API clients (sync and async).

Usage::

    # Sync
    client = VesselClient(api_key="your-api-key")
    vessel = client.vessels.get("9363728")

    # Async
    async with AsyncVesselClient(api_key="your-api-key") as client:
        vessel = await client.vessels.get("9363728")
"""

from __future__ import annotations

import httpx

from ._constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    DEFAULT_USER_AGENT,
)
from ._services import (
    AsyncEmissionsService,
    AsyncLocationService,
    AsyncNavtexService,
    AsyncPortEventsService,
    AsyncPortsService,
    AsyncSearchService,
    AsyncVesselsService,
    EmissionsService,
    LocationService,
    NavtexService,
    PortEventsService,
    PortsService,
    SearchService,
    VesselsService,
)
from ._transport import (
    AsyncAuthTransport,
    AsyncRetryTransport,
    AuthTransport,
    RetryTransport,
)


class VesselClient:
    """Synchronous client for the Vessel Tracking API.

    Args:
        api_key: Bearer token for authentication. Required, must not be empty.
        base_url: API base URL. Defaults to ``https://api.vesselapi.com/v1``.
        timeout: Request timeout in seconds. Defaults to 30.
        max_retries: Maximum retries on 429/5xx. Defaults to 3.
        user_agent: User-Agent header value.
        transport: Custom base ``httpx.BaseTransport`` (auth + retry wrap on top).

    Raises:
        ValueError: If ``api_key`` is empty.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        user_agent: str = DEFAULT_USER_AGENT,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("vesselapi: api_key must not be empty")
        if max_retries < 0:
            max_retries = 0

        base_transport = transport or httpx.HTTPTransport()
        auth_transport = AuthTransport(base_transport, api_key, user_agent)
        retry_transport = RetryTransport(auth_transport, max_retries)

        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            transport=retry_transport,
        )

        self.vessels = VesselsService(self._client)
        self.ports = PortsService(self._client)
        self.port_events = PortEventsService(self._client)
        self.emissions = EmissionsService(self._client)
        self.search = SearchService(self._client)
        self.location = LocationService(self._client)
        self.navtex = NavtexService(self._client)

    def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> VesselClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncVesselClient:
    """Asynchronous client for the Vessel Tracking API.

    Args:
        api_key: Bearer token for authentication. Required, must not be empty.
        base_url: API base URL. Defaults to ``https://api.vesselapi.com/v1``.
        timeout: Request timeout in seconds. Defaults to 30.
        max_retries: Maximum retries on 429/5xx. Defaults to 3.
        user_agent: User-Agent header value.
        transport: Custom base ``httpx.AsyncBaseTransport`` (auth + retry wrap on top).

    Raises:
        ValueError: If ``api_key`` is empty.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        user_agent: str = DEFAULT_USER_AGENT,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("vesselapi: api_key must not be empty")
        if max_retries < 0:
            max_retries = 0

        base_transport = transport or httpx.AsyncHTTPTransport()
        auth_transport = AsyncAuthTransport(base_transport, api_key, user_agent)
        retry_transport = AsyncRetryTransport(auth_transport, max_retries)

        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            transport=retry_transport,
        )

        self.vessels = AsyncVesselsService(self._client)
        self.ports = AsyncPortsService(self._client)
        self.port_events = AsyncPortEventsService(self._client)
        self.emissions = AsyncEmissionsService(self._client)
        self.search = AsyncSearchService(self._client)
        self.location = AsyncLocationService(self._client)
        self.navtex = AsyncNavtexService(self._client)

    async def aclose(self) -> None:
        """Close the underlying HTTP client and release resources."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncVesselClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
