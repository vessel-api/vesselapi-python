"""Vessel Tracking API Python SDK.

Usage::

    from vessel_api_python import VesselClient

    client = VesselClient(api_key="your-api-key")
    result = client.search.vessels(filter_name="Ever Given")
"""

from ._client import AsyncVesselClient, VesselClient
from ._constants import DEFAULT_BASE_URL, VERSION
from ._errors import (
    VesselAPIError,
    VesselAuthError,
    VesselForbiddenError,
    VesselNotFoundError,
    VesselPaymentRequiredError,
    VesselRateLimitError,
    VesselServerError,
)
from ._iterator import AsyncIterator, SyncIterator
from ._models import (
    MODU,
    DGPSStation,
    DGPSStationsWithinLocationResponse,
    FindDGPSStationsResponse,
    FindLightAidsResponse,
    FindMODUsResponse,
    FindPortsResponse,
    FindRadioBeaconsResponse,
    FindVesselsResponse,
    GeoJSON,
    LightAid,
    LightAidsWithinLocationResponse,
    MarineCasualtiesResponse,
    MarineCasualty,
    MODUsWithinLocationResponse,
    Port,
    PortCountry,
    PortEvent,
    PortEventResponse,
    PortEventsResponse,
    PortInboundResponse,
    PortReference,
    PortResponse,
    PortsWithinLocationResponse,
    PositionCheck,
    PreviousPosition,
    RadioBeacon,
    RadioBeaconsWithinLocationResponse,
    ResolutionMeta,
    Vessel,
    VesselEmission,
    VesselEmissionsResponse,
    VesselETA,
    VesselETAResponse,
    VesselFormerName,
    VesselPosition,
    VesselPositionResponse,
    VesselPositionsResponse,
    VesselReference,
    VesselResponse,
    VesselSearchMeta,
    VesselsWithinLocationResponse,
)
from ._services import MultiFilter

__all__ = [
    # Clients
    "VesselClient",
    "AsyncVesselClient",
    # Errors
    "VesselAPIError",
    "VesselAuthError",
    "VesselForbiddenError",
    "VesselNotFoundError",
    "VesselPaymentRequiredError",
    "VesselRateLimitError",
    "VesselServerError",
    # Iterators
    "SyncIterator",
    "AsyncIterator",
    # Constants
    "VERSION",
    "DEFAULT_BASE_URL",
    # Typing helpers
    "MultiFilter",
    # Models — Shared / helper
    "GeoJSON",
    "PortCountry",
    "PortReference",
    "VesselReference",
    "VesselFormerName",
    "ResolutionMeta",
    # Models — Vessel
    "Vessel",
    "VesselResponse",
    "VesselPosition",
    "VesselPositionResponse",
    "PositionCheck",
    "PreviousPosition",
    "VesselPositionsResponse",
    "MarineCasualty",
    "MarineCasualtiesResponse",
    "VesselEmission",
    "VesselEmissionsResponse",
    "VesselETA",
    "VesselETAResponse",
    # Models — Port
    "Port",
    "PortResponse",
    "PortEvent",
    "PortEventResponse",
    "PortEventsResponse",
    "PortInboundResponse",
    # Models — Search
    "VesselSearchMeta",
    "FindVesselsResponse",
    "FindPortsResponse",
    "DGPSStation",
    "FindDGPSStationsResponse",
    "LightAid",
    "FindLightAidsResponse",
    "MODU",
    "FindMODUsResponse",
    "RadioBeacon",
    "FindRadioBeaconsResponse",
    # Models — Location
    "VesselsWithinLocationResponse",
    "PortsWithinLocationResponse",
    "DGPSStationsWithinLocationResponse",
    "LightAidsWithinLocationResponse",
    "MODUsWithinLocationResponse",
    "RadioBeaconsWithinLocationResponse",
]
