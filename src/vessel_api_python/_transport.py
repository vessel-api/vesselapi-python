"""HTTP transport middleware for auth and retry logic."""

from __future__ import annotations

import asyncio
import datetime
import math
import random
import time
from email.utils import parsedate_to_datetime

import httpx

from ._constants import MAX_BACKOFF

# ---------------------------------------------------------------------------
# Auth transports
# ---------------------------------------------------------------------------


class AuthTransport(httpx.BaseTransport):
    """Sync transport that adds Bearer token auth and User-Agent headers."""

    def __init__(self, base: httpx.BaseTransport, api_key: str, user_agent: str) -> None:
        self._base = base
        self._api_key = api_key
        self._user_agent = user_agent

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        request.headers["Authorization"] = f"Bearer {self._api_key}"
        request.headers["User-Agent"] = self._user_agent
        return self._base.handle_request(request)

    def close(self) -> None:
        self._base.close()


class AsyncAuthTransport(httpx.AsyncBaseTransport):
    """Async transport that adds Bearer token auth and User-Agent headers."""

    def __init__(self, base: httpx.AsyncBaseTransport, api_key: str, user_agent: str) -> None:
        self._base = base
        self._api_key = api_key
        self._user_agent = user_agent

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        request.headers["Authorization"] = f"Bearer {self._api_key}"
        request.headers["User-Agent"] = self._user_agent
        return await self._base.handle_async_request(request)

    async def aclose(self) -> None:
        await self._base.aclose()


# ---------------------------------------------------------------------------
# Retry transports
# ---------------------------------------------------------------------------


class RetryTransport(httpx.BaseTransport):
    """Sync transport with retry logic for 429, 5xx, and transient errors.

    Implements exponential backoff with jitter, respects Retry-After headers
    (both seconds and HTTP-date formats), and caps backoff at 30 seconds.
    Only retries non-idempotent methods (POST/PATCH) on 429.
    """

    def __init__(self, base: httpx.BaseTransport, max_retries: int = 3) -> None:
        self._base = base
        self._max_retries = max(max_retries, 0)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        for attempt in range(self._max_retries + 1):
            try:
                response = self._base.handle_request(request)
            except httpx.TransportError:
                # Retry transient network errors for idempotent methods only.
                if attempt >= self._max_retries or not _is_idempotent(request.method):
                    raise
                time.sleep(_calc_exp_backoff(attempt))
                continue

            if not _is_retryable(response.status_code) or attempt >= self._max_retries:
                return response

            # Don't retry non-idempotent methods on 5xx.
            if response.status_code != 429 and not _is_idempotent(request.method):
                return response

            wait = _calc_backoff(attempt, response)
            # Read and discard the body to free the connection.
            response.read()
            response.close()
            time.sleep(wait)

        # Unreachable — the loop always returns.
        raise RuntimeError("vesselapi: retry loop exited unexpectedly")  # pragma: no cover

    def close(self) -> None:
        self._base.close()


class AsyncRetryTransport(httpx.AsyncBaseTransport):
    """Async transport with retry logic for 429, 5xx, and transient errors.

    Same logic as RetryTransport but using asyncio.sleep for async contexts.
    """

    def __init__(self, base: httpx.AsyncBaseTransport, max_retries: int = 3) -> None:
        self._base = base
        self._max_retries = max(max_retries, 0)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._base.handle_async_request(request)
            except httpx.TransportError:
                if attempt >= self._max_retries or not _is_idempotent(request.method):
                    raise
                await asyncio.sleep(_calc_exp_backoff(attempt))
                continue

            if not _is_retryable(response.status_code) or attempt >= self._max_retries:
                return response

            if response.status_code != 429 and not _is_idempotent(request.method):
                return response

            wait = _calc_backoff(attempt, response)
            await response.aread()
            await response.aclose()
            await asyncio.sleep(wait)

        raise RuntimeError("vesselapi: retry loop exited unexpectedly")  # pragma: no cover

    async def aclose(self) -> None:
        await self._base.aclose()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_retryable(status_code: int) -> bool:
    """Return True if the status code warrants a retry."""
    return status_code == 429 or status_code >= 500


def _is_idempotent(method: str) -> bool:
    """Return True for HTTP methods that are safe to retry."""
    return method.upper() in {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}


def _calc_backoff(attempt: int, response: httpx.Response) -> float:
    """Calculate retry wait time, respecting Retry-After header."""
    retry_after = response.headers.get("Retry-After", "")
    if retry_after:
        # Try integer seconds first.
        try:
            seconds = int(retry_after)
            return max(0.0, min(float(seconds), MAX_BACKOFF))
        except ValueError:
            pass
        # Try HTTP-date format (RFC 7231 section 7.1.3).
        try:
            dt = parsedate_to_datetime(retry_after)
            delta = (dt - _utcnow()).total_seconds()
            return max(0.0, min(delta, MAX_BACKOFF))
        except (ValueError, TypeError):
            pass
    return _calc_exp_backoff(attempt)


def _calc_exp_backoff(attempt: int) -> float:
    """Exponential backoff with jitter, capped at MAX_BACKOFF."""
    base = math.pow(2, attempt)
    jitter = random.random() * base  # noqa: S311
    duration = (base + jitter) * 0.5
    return min(duration, MAX_BACKOFF)


def _utcnow() -> datetime.datetime:
    """Return current UTC datetime. Extracted for test patching."""
    return datetime.datetime.now(datetime.timezone.utc)
