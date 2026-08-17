"""Tests for error types and error_from_response."""

from __future__ import annotations

import json

import pytest

from vessel_api_python import (
    VesselAPIError,
    VesselAuthError,
    VesselForbiddenError,
    VesselNotFoundError,
    VesselPaymentRequiredError,
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
        # 409 stands in for "4xx with no dedicated subclass". This used to use
        # 403, which now maps to VesselForbiddenError.
        with pytest.raises(VesselAPIError) as exc_info:
            error_from_response(409, b"")
        assert exc_info.value.status_code == 409
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


class TestPaymentRequiredAndForbidden:
    """402 and 403 are declared in the spec (403 on every path, 402 on
    /vessel/{id}/position) and mean very different things, so callers need to
    tell them apart without string-matching the human-readable message.
    """

    def test_402_raises_payment_required_with_code(self) -> None:
        body = b'{"error":{"type":"payment_required_error","code":"insufficient_credits","message":"Insufficient satellite credits"}}'
        with pytest.raises(VesselPaymentRequiredError) as exc:
            error_from_response(402, body)
        e = exc.value
        assert e.status_code == 402
        assert e.is_payment_required is True
        assert e.is_forbidden is False
        assert e.code == "insufficient_credits"
        assert e.error_type == "payment_required_error"

    def test_403_raises_forbidden_with_code(self) -> None:
        body = b'{"error":{"type":"forbidden_error","code":"feature_not_available","message":"Not on your plan"}}'
        with pytest.raises(VesselForbiddenError) as exc:
            error_from_response(403, body)
        e = exc.value
        assert e.is_forbidden is True
        assert e.is_payment_required is False
        assert e.is_auth_error is False  # distinct from 401
        assert e.code == "feature_not_available"

    def test_existing_codes_unaffected(self) -> None:
        for status, exc_type in ((401, VesselAuthError), (404, VesselNotFoundError), (429, VesselRateLimitError)):
            with pytest.raises(exc_type):
                error_from_response(status, b'{"error":{"message":"x"}}')

    def test_code_is_none_when_absent(self) -> None:
        with pytest.raises(VesselPaymentRequiredError) as exc:
            error_from_response(402, b'{"message":"no structured error"}')
        assert exc.value.code is None
        assert exc.value.error_type is None
