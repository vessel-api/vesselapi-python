"""Tests for error types and error_from_response."""

from __future__ import annotations

import json

import pytest

from vessel_api_python import (
    VesselAPIError,
    VesselAuthError,
    VesselNotFoundError,
    VesselRateLimitError,
    VesselServerError,
)
from vessel_api_python._errors import error_from_response


class TestVesselAPIError:
    """Tests for the base VesselAPIError class."""

    def test_error_has_status_code(self) -> None:
        err = VesselAPIError(404, "Not Found", b"")
        assert err.status_code == 404

    def test_error_has_message(self) -> None:
        err = VesselAPIError(404, "Not Found", b"")
        assert err.message == "Not Found"

    def test_error_has_body(self) -> None:
        body = b'{"error": "details"}'
        err = VesselAPIError(500, "Server Error", body)
        assert err.body == body

    def test_error_str_contains_prefix(self) -> None:
        err = VesselAPIError(404, "Not Found", b"")
        assert "vesselapi:" in str(err)
        assert "404" in str(err)

    def test_is_not_found(self) -> None:
        assert VesselAPIError(404, "", b"").is_not_found is True
        assert VesselAPIError(500, "", b"").is_not_found is False

    def test_is_rate_limited(self) -> None:
        assert VesselAPIError(429, "", b"").is_rate_limited is True
        assert VesselAPIError(500, "", b"").is_rate_limited is False

    def test_is_auth_error(self) -> None:
        assert VesselAPIError(401, "", b"").is_auth_error is True
        assert VesselAPIError(403, "", b"").is_auth_error is False


class TestErrorSubclasses:
    """Tests for specific error subclasses."""

    def test_auth_error_is_vessel_api_error(self) -> None:
        err = VesselAuthError(401, "Unauthorized", b"")
        assert isinstance(err, VesselAPIError)

    def test_not_found_error_is_vessel_api_error(self) -> None:
        err = VesselNotFoundError(404, "Not Found", b"")
        assert isinstance(err, VesselAPIError)

    def test_rate_limit_error_is_vessel_api_error(self) -> None:
        err = VesselRateLimitError(429, "Too Many Requests", b"")
        assert isinstance(err, VesselAPIError)

    def test_server_error_is_vessel_api_error(self) -> None:
        err = VesselServerError(500, "Internal Server Error", b"")
        assert isinstance(err, VesselAPIError)


class TestErrorFromResponse:
    """Tests for the error_from_response helper."""

    def test_2xx_does_not_raise(self) -> None:
        error_from_response(200, b"")
        error_from_response(201, b"")
        error_from_response(204, b"")

    def test_401_raises_auth_error(self) -> None:
        with pytest.raises(VesselAuthError) as exc_info:
            error_from_response(401, b"")
        assert exc_info.value.status_code == 401

    def test_404_raises_not_found_error(self) -> None:
        with pytest.raises(VesselNotFoundError) as exc_info:
            error_from_response(404, b"")
        assert exc_info.value.status_code == 404

    def test_429_raises_rate_limit_error(self) -> None:
        with pytest.raises(VesselRateLimitError) as exc_info:
            error_from_response(429, b"")
        assert exc_info.value.status_code == 429

    def test_500_raises_server_error(self) -> None:
        with pytest.raises(VesselServerError) as exc_info:
            error_from_response(500, b"")
        assert exc_info.value.status_code == 500

    def test_other_4xx_raises_base_error(self) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            error_from_response(403, b"")
        assert exc_info.value.status_code == 403
        assert type(exc_info.value) is VesselAPIError

    def test_parses_nested_json_error(self) -> None:
        """Parses {"error": {"message": "..."}} shape."""
        body = json.dumps({"error": {"message": "Rate limit exceeded"}}).encode()
        with pytest.raises(VesselAPIError) as exc_info:
            error_from_response(429, body)
        assert exc_info.value.message == "Rate limit exceeded"

    def test_parses_flat_json_error(self) -> None:
        """Parses {"message": "..."} shape as fallback."""
        body = json.dumps({"message": "Not authorized"}).encode()
        with pytest.raises(VesselAPIError) as exc_info:
            error_from_response(401, body)
        assert exc_info.value.message == "Not authorized"

    def test_falls_back_to_status_text_for_non_json(self) -> None:
        """Falls back to HTTP status text for non-JSON bodies."""
        with pytest.raises(VesselAPIError) as exc_info:
            error_from_response(500, b"<html>Server Error</html>")
        assert exc_info.value.message == "Internal Server Error"

    def test_falls_back_to_status_text_for_empty_body(self) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            error_from_response(404, b"")
        assert exc_info.value.message == "Not Found"

    def test_body_preserved_on_error(self) -> None:
        body = b'{"error": {"message": "bad request"}}'
        with pytest.raises(VesselAPIError) as exc_info:
            error_from_response(400, body)
        assert exc_info.value.body == body
