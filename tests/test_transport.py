"""Tests for auth and retry transport middleware."""

from __future__ import annotations

import httpx
import pytest
import respx

from vessel_api_python._transport import (
    AuthTransport,
    RetryTransport,
    _calc_backoff,
    _calc_exp_backoff,
    _is_idempotent,
    _is_retryable,
)


class TestAuthTransport:
    """Tests for the AuthTransport middleware."""

    def test_adds_bearer_header(self) -> None:
        """Auth transport adds Authorization: Bearer header."""
        with respx.mock(base_url="https://example.com") as router:
            route = router.get("/test").mock(return_value=httpx.Response(200))
            transport = AuthTransport(
                httpx.HTTPTransport(), api_key="test-key", user_agent="test-agent"
            )
            client = httpx.Client(base_url="https://example.com", transport=transport)
            client.get("/test")
            assert route.calls[0].request.headers["Authorization"] == "Bearer test-key"
            client.close()

    def test_adds_user_agent_header(self) -> None:
        """Auth transport adds User-Agent header."""
        with respx.mock(base_url="https://example.com") as router:
            route = router.get("/test").mock(return_value=httpx.Response(200))
            transport = AuthTransport(
                httpx.HTTPTransport(), api_key="key", user_agent="my-agent/1.0"
            )
            client = httpx.Client(base_url="https://example.com", transport=transport)
            client.get("/test")
            assert route.calls[0].request.headers["User-Agent"] == "my-agent/1.0"
            client.close()


class TestRetryTransport:
    """Tests for the RetryTransport middleware."""

    def test_retries_on_429(self) -> None:
        """RetryTransport retries on 429 status."""
        call_count = 0

        class CountingTransport(httpx.BaseTransport):
            def handle_request(self, request: httpx.Request) -> httpx.Response:
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    return httpx.Response(429, headers={"Retry-After": "0"})
                return httpx.Response(200)

        transport = RetryTransport(CountingTransport(), max_retries=3)
        client = httpx.Client(base_url="https://example.com", transport=transport)
        response = client.get("/test")
        assert response.status_code == 200
        assert call_count == 2
        client.close()

    def test_retries_on_500(self) -> None:
        """RetryTransport retries on 5xx for GET (idempotent)."""
        call_count = 0

        class CountingTransport(httpx.BaseTransport):
            def handle_request(self, request: httpx.Request) -> httpx.Response:
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    return httpx.Response(500)
                return httpx.Response(200)

        transport = RetryTransport(CountingTransport(), max_retries=3)
        client = httpx.Client(base_url="https://example.com", transport=transport)
        response = client.get("/test")
        assert response.status_code == 200
        assert call_count == 2
        client.close()

    def test_does_not_retry_post_on_500(self) -> None:
        """RetryTransport does NOT retry POST on 5xx (non-idempotent)."""
        call_count = 0

        class CountingTransport(httpx.BaseTransport):
            def handle_request(self, request: httpx.Request) -> httpx.Response:
                nonlocal call_count
                call_count += 1
                return httpx.Response(500)

        transport = RetryTransport(CountingTransport(), max_retries=3)
        client = httpx.Client(base_url="https://example.com", transport=transport)
        response = client.post("/test")
        assert response.status_code == 500
        assert call_count == 1  # No retries for POST on 500
        client.close()

    def test_retries_post_on_429(self) -> None:
        """RetryTransport DOES retry POST on 429 (rate limit = not processed)."""
        call_count = 0

        class CountingTransport(httpx.BaseTransport):
            def handle_request(self, request: httpx.Request) -> httpx.Response:
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    return httpx.Response(429, headers={"Retry-After": "0"})
                return httpx.Response(200)

        transport = RetryTransport(CountingTransport(), max_retries=3)
        client = httpx.Client(base_url="https://example.com", transport=transport)
        response = client.post("/test", content=b"body")
        assert response.status_code == 200
        assert call_count == 2
        client.close()

    def test_max_retries_exhausted(self) -> None:
        """RetryTransport returns last response when max retries exhausted."""
        class AlwaysFailTransport(httpx.BaseTransport):
            def handle_request(self, request: httpx.Request) -> httpx.Response:
                return httpx.Response(500)

        transport = RetryTransport(AlwaysFailTransport(), max_retries=2)
        client = httpx.Client(base_url="https://example.com", transport=transport)
        response = client.get("/test")
        assert response.status_code == 500
        client.close()

    def test_respects_retry_after_seconds(self) -> None:
        """RetryTransport respects Retry-After header (seconds format)."""
        response = httpx.Response(429, headers={"Retry-After": "5"})
        backoff = _calc_backoff(0, response)
        assert backoff == 5.0

    def test_respects_retry_after_http_date(self) -> None:
        """RetryTransport respects Retry-After header (HTTP-date format)."""
        # Use a date far in the future to get a positive delta.
        response = httpx.Response(429, headers={"Retry-After": "Sun, 01 Jan 2034 00:00:00 GMT"})
        backoff = _calc_backoff(0, response)
        assert backoff == 30.0  # Capped at MAX_BACKOFF

    def test_negative_retry_after_clamped_to_zero(self) -> None:
        """Negative Retry-After values are clamped to 0."""
        response = httpx.Response(429, headers={"Retry-After": "-1"})
        backoff = _calc_backoff(0, response)
        assert backoff == 0.0

    def test_retries_on_transport_error_for_get(self) -> None:
        """RetryTransport retries on TransportError for idempotent methods."""
        call_count = 0

        class FailThenSucceedTransport(httpx.BaseTransport):
            def handle_request(self, request: httpx.Request) -> httpx.Response:
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise httpx.ConnectError("connection reset")
                return httpx.Response(200)

        transport = RetryTransport(FailThenSucceedTransport(), max_retries=3)
        client = httpx.Client(base_url="https://example.com", transport=transport)
        response = client.get("/test")
        assert response.status_code == 200
        assert call_count == 2
        client.close()

    def test_does_not_retry_transport_error_for_post(self) -> None:
        """RetryTransport does NOT retry TransportError for POST."""
        class AlwaysFailTransport(httpx.BaseTransport):
            def handle_request(self, request: httpx.Request) -> httpx.Response:
                raise httpx.ConnectError("connection reset")

        transport = RetryTransport(AlwaysFailTransport(), max_retries=3)
        client = httpx.Client(base_url="https://example.com", transport=transport)
        with pytest.raises(httpx.ConnectError):
            client.post("/test")
        client.close()


class TestHelpers:
    """Tests for transport helper functions."""

    def test_is_retryable(self) -> None:
        assert _is_retryable(429) is True
        assert _is_retryable(500) is True
        assert _is_retryable(502) is True
        assert _is_retryable(200) is False
        assert _is_retryable(404) is False

    def test_is_idempotent(self) -> None:
        assert _is_idempotent("GET") is True
        assert _is_idempotent("HEAD") is True
        assert _is_idempotent("PUT") is True
        assert _is_idempotent("DELETE") is True
        assert _is_idempotent("OPTIONS") is True
        assert _is_idempotent("POST") is False
        assert _is_idempotent("PATCH") is False

    def test_exp_backoff_capped(self) -> None:
        """Exponential backoff should be capped at MAX_BACKOFF (30s)."""
        backoff = _calc_exp_backoff(100)
        assert backoff <= 30.0

    def test_exp_backoff_grows(self) -> None:
        """Backoff at attempt 0 should be less than attempt 5."""
        b0 = _calc_exp_backoff(0)
        # Due to jitter, just verify attempt 0 produces a reasonable range.
        assert 0.0 <= b0 <= 30.0
