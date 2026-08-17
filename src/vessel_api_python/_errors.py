"""Error types for the Vessel API Python SDK."""

from __future__ import annotations

import http
import json


class VesselAPIError(Exception):
    """Base error for all Vessel API errors.

    Attributes:
        status_code: The HTTP status code from the response.
        message: A human-readable error message.
        body: The raw response body bytes, available for re-parsing.
        code: The API's machine-readable error code (e.g. ``insufficient_credits``,
            ``feature_not_available``), or None if the response carried none.
            Branch on this rather than on ``message``, which may be reworded.
        error_type: The API's error type (e.g. ``payment_required_error``), or None.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        body: bytes = b"",
        code: str | None = None,
        error_type: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.body = body
        self.code = code
        self.error_type = error_type
        super().__init__(f"vesselapi: {message} (status {status_code})")

    @property
    def is_not_found(self) -> bool:
        """True if the error is a 404 Not Found response."""
        return self.status_code == 404

    @property
    def is_rate_limited(self) -> bool:
        """True if the error is a 429 Too Many Requests response."""
        return self.status_code == 429

    @property
    def is_auth_error(self) -> bool:
        """True if the error is a 401 Unauthorized response."""
        return self.status_code == 401

    @property
    def is_payment_required(self) -> bool:
        """True if the error is a 402 Payment Required response.

        Returned when a satellite-backed call is made with no satellite credits
        left. Retry without ``filter_sat`` to serve stored data instead, or top
        up the balance.
        """
        return self.status_code == 402

    @property
    def is_forbidden(self) -> bool:
        """True if the error is a 403 Forbidden response.

        Distinct from 401: the key is valid but not permitted. Check ``code`` to
        tell a temporarily suspended key from a feature that is not on the
        caller's plan.
        """
        return self.status_code == 403


class VesselAuthError(VesselAPIError):
    """Raised on 401 Unauthorized responses."""


class VesselPaymentRequiredError(VesselAPIError):
    """Raised on 402 Payment Required responses (satellite credits exhausted)."""


class VesselForbiddenError(VesselAPIError):
    """Raised on 403 Forbidden responses (key suspended, or feature not on plan)."""


class VesselNotFoundError(VesselAPIError):
    """Raised on 404 Not Found responses."""


class VesselRateLimitError(VesselAPIError):
    """Raised on 429 Too Many Requests responses."""


class VesselServerError(VesselAPIError):
    """Raised on 5xx server error responses."""


def error_from_response(
    status_code: int,
    body: bytes,
    headers: dict[str, str] | None = None,
) -> None:
    """Raise a VesselAPIError if the response indicates an error.

    Checks for success using ``200 <= status_code < 300``. On error,
    attempts to parse a human-readable message from the JSON body using
    multiple known shapes, falling back to the HTTP status text.

    Args:
        status_code: The HTTP response status code.
        body: The raw response body bytes.
        headers: Optional response headers (unused currently, reserved).

    Raises:
        VesselAuthError: On 401 responses.
        VesselPaymentRequiredError: On 402 responses (satellite credits exhausted).
        VesselForbiddenError: On 403 responses (suspended key, or feature not on plan).
        VesselNotFoundError: On 404 responses.
        VesselRateLimitError: On 429 responses.
        VesselServerError: On 5xx responses.
        VesselAPIError: On all other non-2xx responses.
    """
    if 200 <= status_code < 300:
        return

    # Try to extract a human-readable message from the response body.
    msg = _status_text(status_code)
    code: str | None = None
    error_type: str | None = None
    if body:
        try:
            data = json.loads(body)
            # Try {"error": {"message": "..."}} (Vessel API standard shape).
            nested_msg = _get_nested(data, "error", "message")
            if nested_msg:
                msg = nested_msg
            else:
                # Try {"message": "..."} (common alternative shape).
                flat_msg = data.get("message") if isinstance(data, dict) else None
                if flat_msg and isinstance(flat_msg, str):
                    msg = flat_msg
            # The API also sends machine-readable discriminators. Expose them:
            # branching on `message` breaks whenever the wording changes.
            code = _get_nested(data, "error", "code")
            error_type = _get_nested(data, "error", "type")
            # If both fail, msg stays as HTTP status text.
            # Raw body is always available in VesselAPIError.body.
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass

    # Return the appropriate subclass based on status code.
    error_cls: type[VesselAPIError]
    if status_code == 401:
        error_cls = VesselAuthError
    elif status_code == 402:
        error_cls = VesselPaymentRequiredError
    elif status_code == 403:
        error_cls = VesselForbiddenError
    elif status_code == 404:
        error_cls = VesselNotFoundError
    elif status_code == 429:
        error_cls = VesselRateLimitError
    elif status_code >= 500:
        error_cls = VesselServerError
    else:
        error_cls = VesselAPIError

    raise error_cls(status_code=status_code, message=msg, body=body, code=code, error_type=error_type)


def _get_nested(data: dict[str, object] | list[object] | None, *keys: str) -> str | None:
    """Safely traverse nested dicts to extract a string value."""
    current: object = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current if isinstance(current, str) else None


def _status_text(status_code: int) -> str:
    """Return the HTTP status text for a given code."""
    try:
        return http.HTTPStatus(status_code).phrase
    except ValueError:
        return f"HTTP {status_code}"
