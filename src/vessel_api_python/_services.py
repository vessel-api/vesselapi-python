"""Service classes wrapping Vessel API endpoints.

Each service groups related API endpoints and provides typed methods with
sensible defaults. All endpoints that require ``filter_id_type`` default
to ``"imo"`` to match the Go SDK behaviour.

Services come in sync and async variants. The async variants have the same
method signatures but use ``await`` for HTTP calls.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._errors import error_from_response
from ._iterator import AsyncIterator, SyncIterator
from ._models import (
    MODU,
    ClassificationResponse,
    DGPSStation,
    DGPSStationsWithinLocationResponse,
    FindDGPSStationsResponse,
    FindLightAidsResponse,
    FindMODUsResponse,
    FindPortsResponse,
    FindRadioBeaconsResponse,
    FindVesselsResponse,
    LightAid,
    LightAidsWithinLocationResponse,
    MarineCasualtiesResponse,
    MarineCasualty,
    MODUsWithinLocationResponse,
    Navtex,
    NavtexMessagesResponse,
    Port,
    PortEvent,
    PortEventResponse,
    PortEventsResponse,
    PortInboundResponse,
    PortResponse,
    PortsWithinLocationResponse,
    RadioBeacon,
    RadioBeaconsWithinLocationResponse,
    TypesInspectionDetailResponse,
    TypesInspectionsResponse,
    TypesOwnershipResponse,
    Vessel,
    VesselEmission,
    VesselEmissionsResponse,
    VesselETA,
    VesselETAResponse,
    VesselPosition,
    VesselPositionResponse,
    VesselPositionsResponse,
    VesselResponse,
    VesselsWithinLocationResponse,
)

if TYPE_CHECKING:
    import httpx


def _strip_none(params: dict[str, Any]) -> dict[str, Any]:
    """Remove keys with None values from a dict of query params."""
    return {k: v for k, v in params.items() if v is not None}


# ===================================================================
# Sync services
# ===================================================================


class VesselsService:
    """Vessel-related API endpoints (sync)."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def get(self, vessel_id: str, *, filter_id_type: str = "imo") -> VesselResponse:
        """Retrieve vessel details by ID (IMO or MMSI)."""
        r = self._client.get(f"/vessel/{vessel_id}", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return VesselResponse.model_validate(r.json())

    def position(self, vessel_id: str, *, filter_id_type: str = "imo") -> VesselPositionResponse:
        """Retrieve the latest position for a vessel."""
        r = self._client.get(f"/vessel/{vessel_id}/position", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return VesselPositionResponse.model_validate(r.json())

    def casualties(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None, pagination_next_token: str | None = None) -> MarineCasualtiesResponse:
        """Retrieve marine casualty records for a vessel."""
        r = self._client.get(f"/vessel/{vessel_id}/casualties", params=_strip_none({"filter.idType": filter_id_type, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return MarineCasualtiesResponse.model_validate(r.json())

    def classification(self, vessel_id: str, *, filter_id_type: str = "imo") -> ClassificationResponse:
        """Retrieve classification data for a vessel."""
        r = self._client.get(f"/vessel/{vessel_id}/classification", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return ClassificationResponse.model_validate(r.json())

    def emissions(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselEmissionsResponse:
        """Retrieve emissions data for a vessel."""
        r = self._client.get(f"/vessel/{vessel_id}/emissions", params=_strip_none({"filter.idType": filter_id_type, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselEmissionsResponse.model_validate(r.json())

    def eta(self, vessel_id: str, *, filter_id_type: str = "imo") -> VesselETAResponse:
        """Retrieve the estimated time of arrival for a vessel."""
        r = self._client.get(f"/vessel/{vessel_id}/eta", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return VesselETAResponse.model_validate(r.json())

    def inspections(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None, pagination_next_token: str | None = None) -> TypesInspectionsResponse:
        """Retrieve inspection records for a vessel."""
        r = self._client.get(f"/vessel/{vessel_id}/inspections", params=_strip_none({"filter.idType": filter_id_type, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return TypesInspectionsResponse.model_validate(r.json())

    def inspection_detail(self, vessel_id: str, detail_id: str, *, filter_id_type: str = "imo") -> TypesInspectionDetailResponse:
        """Retrieve detailed inspection data."""
        r = self._client.get(f"/vessel/{vessel_id}/inspections/{detail_id}", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return TypesInspectionDetailResponse.model_validate(r.json())

    def ownership(self, vessel_id: str, *, filter_id_type: str = "imo") -> TypesOwnershipResponse:
        """Retrieve ownership data for a vessel."""
        r = self._client.get(f"/vessel/{vessel_id}/ownership", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return TypesOwnershipResponse.model_validate(r.json())

    def positions(self, *, filter_id_type: str = "imo", filter_ids: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselPositionsResponse:
        """Retrieve positions for multiple vessels."""
        r = self._client.get("/vessels/positions", params=_strip_none({"filter.idType": filter_id_type, "filter.ids": filter_ids, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselPositionsResponse.model_validate(r.json())

    # --- Iterators ---

    def all_casualties(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None) -> SyncIterator[MarineCasualty]:
        """Iterate over all casualties for a vessel across pages."""
        token: str | None = None
        def fetch() -> tuple[list[MarineCasualty], str | None]:
            nonlocal token
            resp = self.casualties(vessel_id, filter_id_type=filter_id_type, pagination_limit=pagination_limit, pagination_next_token=token)
            token = resp.next_token
            return resp.casualties or [], token
        return SyncIterator(fetch)

    def all_emissions(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None) -> SyncIterator[VesselEmission]:
        """Iterate over all emissions for a vessel across pages."""
        token: str | None = None
        def fetch() -> tuple[list[VesselEmission], str | None]:
            nonlocal token
            resp = self.emissions(vessel_id, filter_id_type=filter_id_type, pagination_limit=pagination_limit, pagination_next_token=token)
            token = resp.next_token
            return resp.emissions or [], token
        return SyncIterator(fetch)

    def all_positions(self, *, filter_id_type: str = "imo", filter_ids: str | None = None, pagination_limit: int | None = None) -> SyncIterator[VesselPosition]:
        """Iterate over all positions for multiple vessels across pages."""
        token: str | None = None
        def fetch() -> tuple[list[VesselPosition], str | None]:
            nonlocal token
            resp = self.positions(filter_id_type=filter_id_type, filter_ids=filter_ids, pagination_limit=pagination_limit, pagination_next_token=token)
            token = resp.next_token
            return resp.vessel_positions or [], token
        return SyncIterator(fetch)


class PortsService:
    """Port lookup endpoints (sync)."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def get(self, unlocode: str) -> PortResponse:
        """Retrieve a port by its UN/LOCODE."""
        r = self._client.get(f"/port/{unlocode}")
        error_from_response(r.status_code, r.content)
        return PortResponse.model_validate(r.json())

    def inbound(self, unlocode: str, *, eta_from: str, eta_to: str, time_from: str | None = None, time_to: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortInboundResponse:
        """Retrieve vessels heading to a port."""
        r = self._client.get(f"/port/{unlocode}/inbound", params=_strip_none({"filter.etaFrom": eta_from, "filter.etaTo": eta_to, "time.from": time_from, "time.to": time_to, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortInboundResponse.model_validate(r.json())

    def inbound_all(self, unlocode: str, *, eta_from: str, eta_to: str, time_from: str | None = None, time_to: str | None = None, pagination_limit: int | None = None) -> SyncIterator[VesselETA]:
        """Iterate over all inbound vessels for a port across pages."""
        token: str | None = None
        def fetch() -> tuple[list[VesselETA], str | None]:
            nonlocal token
            resp = self.inbound(unlocode, eta_from=eta_from, eta_to=eta_to, time_from=time_from, time_to=time_to, pagination_limit=pagination_limit, pagination_next_token=token)
            token = resp.next_token
            return resp.vessel_etas or [], token
        return SyncIterator(fetch)


class PortEventsService:
    """Port event endpoints (sync)."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self, *, time_from: str | None = None, time_to: str | None = None, filter_country: str | None = None, filter_unlocode: str | None = None, filter_event_type: str | None = None, filter_vessel_name: str | None = None, filter_port_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events with optional filtering."""
        r = self._client.get("/portevents", params=_strip_none({"time.from": time_from, "time.to": time_to, "filter.country": filter_country, "filter.unlocode": filter_unlocode, "filter.eventType": filter_event_type, "filter.vesselName": filter_vessel_name, "filter.portName": filter_port_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    def by_port(self, unlocode: str, *, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events for a specific port by UNLOCODE."""
        r = self._client.get(f"/portevents/port/{unlocode}", params=_strip_none({"pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    def by_ports(self, *, filter_port_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events by port name search."""
        r = self._client.get("/portevents/ports", params=_strip_none({"filter.portName": filter_port_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    def by_vessel(self, vessel_id: str, *, filter_id_type: str = "imo", filter_event_type: str | None = None, filter_sort_order: str | None = None, time_from: str | None = None, time_to: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events for a specific vessel."""
        r = self._client.get(f"/portevents/vessel/{vessel_id}", params=_strip_none({"filter.idType": filter_id_type, "filter.eventType": filter_event_type, "filter.sortOrder": filter_sort_order, "time.from": time_from, "time.to": time_to, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    def last_by_vessel(self, vessel_id: str, *, filter_id_type: str = "imo") -> PortEventResponse:
        """Retrieve the last port event for a vessel."""
        r = self._client.get(f"/portevents/vessel/{vessel_id}/last", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return PortEventResponse.model_validate(r.json())

    def by_vessels(self, *, filter_vessel_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events by vessel name search."""
        r = self._client.get("/portevents/vessels", params=_strip_none({"filter.vesselName": filter_vessel_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    # --- Iterators ---

    def list_all(self, **kwargs: Any) -> SyncIterator[PortEvent]:
        """Iterate over all port events across pages."""
        token: str | None = None
        def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = self.list(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return SyncIterator(fetch)

    def all_by_port(self, unlocode: str, **kwargs: Any) -> SyncIterator[PortEvent]:
        """Iterate over all port events for a specific port."""
        token: str | None = None
        def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = self.by_port(unlocode, **kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return SyncIterator(fetch)

    def all_by_ports(self, **kwargs: Any) -> SyncIterator[PortEvent]:
        """Iterate over all port events by port name search."""
        token: str | None = None
        def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = self.by_ports(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return SyncIterator(fetch)

    def all_by_vessel(self, vessel_id: str, **kwargs: Any) -> SyncIterator[PortEvent]:
        """Iterate over all port events for a vessel."""
        token: str | None = None
        def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = self.by_vessel(vessel_id, **kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return SyncIterator(fetch)

    def all_by_vessels(self, **kwargs: Any) -> SyncIterator[PortEvent]:
        """Iterate over all port events by vessel name search."""
        token: str | None = None
        def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = self.by_vessels(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return SyncIterator(fetch)


class EmissionsService:
    """Emissions endpoints (sync)."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self, *, filter_period: int | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselEmissionsResponse:
        """Retrieve vessel emissions data."""
        r = self._client.get("/emissions", params=_strip_none({"filter.period": filter_period, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselEmissionsResponse.model_validate(r.json())

    def list_all(self, **kwargs: Any) -> SyncIterator[VesselEmission]:
        """Iterate over all emissions across pages."""
        token: str | None = None
        def fetch() -> tuple[list[VesselEmission], str | None]:
            nonlocal token
            resp = self.list(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.emissions or [], token
        return SyncIterator(fetch)


class SearchService:
    """Search endpoints (sync)."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def vessels(self, *, filter_name: str | None = None, filter_imo: str | None = None, filter_mmsi: str | None = None, filter_flag: str | None = None, filter_vessel_type: str | None = None, filter_callsign: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindVesselsResponse:
        """Search for vessels by name, callsign, flag, type, and other filters."""
        r = self._client.get("/search/vessels", params=_strip_none({"filter.name": filter_name, "filter.imo": filter_imo, "filter.mmsi": filter_mmsi, "filter.flag": filter_flag, "filter.vesselType": filter_vessel_type, "filter.callsign": filter_callsign, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindVesselsResponse.model_validate(r.json())

    def ports(self, *, filter_name: str | None = None, filter_country: str | None = None, filter_port_type: str | None = None, filter_region: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindPortsResponse:
        """Search for ports by name, country, type, region, and other filters."""
        r = self._client.get("/search/ports", params=_strip_none({"filter.name": filter_name, "filter.country": filter_country, "filter.type": filter_port_type, "filter.region": filter_region, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindPortsResponse.model_validate(r.json())

    def dgps(self, *, filter_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindDGPSStationsResponse:
        """Search for DGPS stations by name."""
        r = self._client.get("/search/dgps", params=_strip_none({"filter.name": filter_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindDGPSStationsResponse.model_validate(r.json())

    def light_aids(self, *, filter_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindLightAidsResponse:
        """Search for light aids by name."""
        r = self._client.get("/search/lightaids", params=_strip_none({"filter.name": filter_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindLightAidsResponse.model_validate(r.json())

    def modus(self, *, filter_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindMODUsResponse:
        """Search for MODUs (Mobile Offshore Drilling Units) by name."""
        r = self._client.get("/search/modus", params=_strip_none({"filter.name": filter_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindMODUsResponse.model_validate(r.json())

    def radio_beacons(self, *, filter_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindRadioBeaconsResponse:
        """Search for radio beacons by name."""
        r = self._client.get("/search/radiobeacons", params=_strip_none({"filter.name": filter_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindRadioBeaconsResponse.model_validate(r.json())

    # --- Iterators ---

    def all_vessels(self, **kwargs: Any) -> SyncIterator[Vessel]:
        """Iterate over all vessel search results across pages."""
        token: str | None = None
        def fetch() -> tuple[list[Vessel], str | None]:
            nonlocal token
            resp = self.vessels(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.vessels or [], token
        return SyncIterator(fetch)

    def all_ports(self, **kwargs: Any) -> SyncIterator[Port]:
        """Iterate over all port search results across pages."""
        token: str | None = None
        def fetch() -> tuple[list[Port], str | None]:
            nonlocal token
            resp = self.ports(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.ports or [], token
        return SyncIterator(fetch)

    def all_dgps(self, **kwargs: Any) -> SyncIterator[DGPSStation]:
        """Iterate over all DGPS station search results."""
        token: str | None = None
        def fetch() -> tuple[list[DGPSStation], str | None]:
            nonlocal token
            resp = self.dgps(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.dgps_stations or [], token
        return SyncIterator(fetch)

    def all_light_aids(self, **kwargs: Any) -> SyncIterator[LightAid]:
        """Iterate over all light aid search results."""
        token: str | None = None
        def fetch() -> tuple[list[LightAid], str | None]:
            nonlocal token
            resp = self.light_aids(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.light_aids or [], token
        return SyncIterator(fetch)

    def all_modus(self, **kwargs: Any) -> SyncIterator[MODU]:
        """Iterate over all MODU search results."""
        token: str | None = None
        def fetch() -> tuple[list[MODU], str | None]:
            nonlocal token
            resp = self.modus(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.modus or [], token
        return SyncIterator(fetch)

    def all_radio_beacons(self, **kwargs: Any) -> SyncIterator[RadioBeacon]:
        """Iterate over all radio beacon search results."""
        token: str | None = None
        def fetch() -> tuple[list[RadioBeacon], str | None]:
            nonlocal token
            resp = self.radio_beacons(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.radio_beacons or [], token
        return SyncIterator(fetch)


class LocationService:
    """Location-based query endpoints (sync)."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def vessels_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselsWithinLocationResponse:
        """Retrieve vessel positions within a bounding box."""
        r = self._client.get("/location/vessels/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselsWithinLocationResponse.model_validate(r.json())

    def vessels_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselsWithinLocationResponse:
        """Retrieve vessel positions within a radius."""
        r = self._client.get("/location/vessels/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselsWithinLocationResponse.model_validate(r.json())

    def ports_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortsWithinLocationResponse:
        """Retrieve ports within a bounding box."""
        r = self._client.get("/location/ports/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortsWithinLocationResponse.model_validate(r.json())

    def ports_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortsWithinLocationResponse:
        """Retrieve ports within a radius."""
        r = self._client.get("/location/ports/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortsWithinLocationResponse.model_validate(r.json())

    def dgps_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> DGPSStationsWithinLocationResponse:
        """Retrieve DGPS stations within a bounding box."""
        r = self._client.get("/location/dgps/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return DGPSStationsWithinLocationResponse.model_validate(r.json())

    def dgps_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> DGPSStationsWithinLocationResponse:
        """Retrieve DGPS stations within a radius."""
        r = self._client.get("/location/dgps/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return DGPSStationsWithinLocationResponse.model_validate(r.json())

    def light_aids_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> LightAidsWithinLocationResponse:
        """Retrieve light aids within a bounding box."""
        r = self._client.get("/location/lightaids/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return LightAidsWithinLocationResponse.model_validate(r.json())

    def light_aids_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> LightAidsWithinLocationResponse:
        """Retrieve light aids within a radius."""
        r = self._client.get("/location/lightaids/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return LightAidsWithinLocationResponse.model_validate(r.json())

    def modus_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> MODUsWithinLocationResponse:
        """Retrieve MODUs within a bounding box."""
        r = self._client.get("/location/modu/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return MODUsWithinLocationResponse.model_validate(r.json())

    def modus_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> MODUsWithinLocationResponse:
        """Retrieve MODUs within a radius."""
        r = self._client.get("/location/modu/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return MODUsWithinLocationResponse.model_validate(r.json())

    def radio_beacons_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> RadioBeaconsWithinLocationResponse:
        """Retrieve radio beacons within a bounding box."""
        r = self._client.get("/location/radiobeacons/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return RadioBeaconsWithinLocationResponse.model_validate(r.json())

    def radio_beacons_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> RadioBeaconsWithinLocationResponse:
        """Retrieve radio beacons within a radius."""
        r = self._client.get("/location/radiobeacons/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return RadioBeaconsWithinLocationResponse.model_validate(r.json())

    # --- Iterators ---

    def all_vessels_bounding_box(self, **kwargs: Any) -> SyncIterator[VesselPosition]:
        """Iterate over all vessel positions in a bounding box."""
        token: str | None = None
        def fetch() -> tuple[list[VesselPosition], str | None]:
            nonlocal token
            resp = self.vessels_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.vessels or [], token
        return SyncIterator(fetch)

    def all_vessels_radius(self, **kwargs: Any) -> SyncIterator[VesselPosition]:
        """Iterate over all vessel positions within a radius."""
        token: str | None = None
        def fetch() -> tuple[list[VesselPosition], str | None]:
            nonlocal token
            resp = self.vessels_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.vessels or [], token
        return SyncIterator(fetch)

    def all_ports_bounding_box(self, **kwargs: Any) -> SyncIterator[Port]:
        """Iterate over all ports in a bounding box."""
        token: str | None = None
        def fetch() -> tuple[list[Port], str | None]:
            nonlocal token
            resp = self.ports_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.ports or [], token
        return SyncIterator(fetch)

    def all_ports_radius(self, **kwargs: Any) -> SyncIterator[Port]:
        """Iterate over all ports within a radius."""
        token: str | None = None
        def fetch() -> tuple[list[Port], str | None]:
            nonlocal token
            resp = self.ports_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.ports or [], token
        return SyncIterator(fetch)

    def all_dgps_bounding_box(self, **kwargs: Any) -> SyncIterator[DGPSStation]:
        """Iterate over all DGPS stations in a bounding box."""
        token: str | None = None
        def fetch() -> tuple[list[DGPSStation], str | None]:
            nonlocal token
            resp = self.dgps_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.dgps_stations or [], token
        return SyncIterator(fetch)

    def all_dgps_radius(self, **kwargs: Any) -> SyncIterator[DGPSStation]:
        """Iterate over all DGPS stations within a radius."""
        token: str | None = None
        def fetch() -> tuple[list[DGPSStation], str | None]:
            nonlocal token
            resp = self.dgps_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.dgps_stations or [], token
        return SyncIterator(fetch)

    def all_light_aids_bounding_box(self, **kwargs: Any) -> SyncIterator[LightAid]:
        """Iterate over all light aids in a bounding box."""
        token: str | None = None
        def fetch() -> tuple[list[LightAid], str | None]:
            nonlocal token
            resp = self.light_aids_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.light_aids or [], token
        return SyncIterator(fetch)

    def all_light_aids_radius(self, **kwargs: Any) -> SyncIterator[LightAid]:
        """Iterate over all light aids within a radius."""
        token: str | None = None
        def fetch() -> tuple[list[LightAid], str | None]:
            nonlocal token
            resp = self.light_aids_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.light_aids or [], token
        return SyncIterator(fetch)

    def all_modus_bounding_box(self, **kwargs: Any) -> SyncIterator[MODU]:
        """Iterate over all MODUs in a bounding box."""
        token: str | None = None
        def fetch() -> tuple[list[MODU], str | None]:
            nonlocal token
            resp = self.modus_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.modus or [], token
        return SyncIterator(fetch)

    def all_modus_radius(self, **kwargs: Any) -> SyncIterator[MODU]:
        """Iterate over all MODUs within a radius."""
        token: str | None = None
        def fetch() -> tuple[list[MODU], str | None]:
            nonlocal token
            resp = self.modus_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.modus or [], token
        return SyncIterator(fetch)

    def all_radio_beacons_bounding_box(self, **kwargs: Any) -> SyncIterator[RadioBeacon]:
        """Iterate over all radio beacons in a bounding box."""
        token: str | None = None
        def fetch() -> tuple[list[RadioBeacon], str | None]:
            nonlocal token
            resp = self.radio_beacons_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.radio_beacons or [], token
        return SyncIterator(fetch)

    def all_radio_beacons_radius(self, **kwargs: Any) -> SyncIterator[RadioBeacon]:
        """Iterate over all radio beacons within a radius."""
        token: str | None = None
        def fetch() -> tuple[list[RadioBeacon], str | None]:
            nonlocal token
            resp = self.radio_beacons_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.radio_beacons or [], token
        return SyncIterator(fetch)


class NavtexService:
    """NAVTEX message endpoints (sync)."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def list(self, *, time_from: str | None = None, time_to: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> NavtexMessagesResponse:
        """Retrieve NAVTEX maritime safety messages."""
        r = self._client.get("/navtex", params=_strip_none({"time.from": time_from, "time.to": time_to, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return NavtexMessagesResponse.model_validate(r.json())

    def list_all(self, **kwargs: Any) -> SyncIterator[Navtex]:
        """Iterate over all NAVTEX messages across pages."""
        token: str | None = None
        def fetch() -> tuple[list[Navtex], str | None]:
            nonlocal token
            resp = self.list(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.navtex_messages or [], token
        return SyncIterator(fetch)


# ===================================================================
# Async services
# ===================================================================


class AsyncVesselsService:
    """Vessel-related API endpoints (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get(self, vessel_id: str, *, filter_id_type: str = "imo") -> VesselResponse:
        """Retrieve vessel details by ID (IMO or MMSI)."""
        r = await self._client.get(f"/vessel/{vessel_id}", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return VesselResponse.model_validate(r.json())

    async def position(self, vessel_id: str, *, filter_id_type: str = "imo") -> VesselPositionResponse:
        """Retrieve the latest position for a vessel."""
        r = await self._client.get(f"/vessel/{vessel_id}/position", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return VesselPositionResponse.model_validate(r.json())

    async def casualties(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None, pagination_next_token: str | None = None) -> MarineCasualtiesResponse:
        """Retrieve marine casualty records for a vessel."""
        r = await self._client.get(f"/vessel/{vessel_id}/casualties", params=_strip_none({"filter.idType": filter_id_type, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return MarineCasualtiesResponse.model_validate(r.json())

    async def classification(self, vessel_id: str, *, filter_id_type: str = "imo") -> ClassificationResponse:
        """Retrieve classification data for a vessel."""
        r = await self._client.get(f"/vessel/{vessel_id}/classification", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return ClassificationResponse.model_validate(r.json())

    async def emissions(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselEmissionsResponse:
        """Retrieve emissions data for a vessel."""
        r = await self._client.get(f"/vessel/{vessel_id}/emissions", params=_strip_none({"filter.idType": filter_id_type, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselEmissionsResponse.model_validate(r.json())

    async def eta(self, vessel_id: str, *, filter_id_type: str = "imo") -> VesselETAResponse:
        """Retrieve the estimated time of arrival for a vessel."""
        r = await self._client.get(f"/vessel/{vessel_id}/eta", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return VesselETAResponse.model_validate(r.json())

    async def inspections(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None, pagination_next_token: str | None = None) -> TypesInspectionsResponse:
        """Retrieve inspection records for a vessel."""
        r = await self._client.get(f"/vessel/{vessel_id}/inspections", params=_strip_none({"filter.idType": filter_id_type, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return TypesInspectionsResponse.model_validate(r.json())

    async def inspection_detail(self, vessel_id: str, detail_id: str, *, filter_id_type: str = "imo") -> TypesInspectionDetailResponse:
        """Retrieve detailed inspection data."""
        r = await self._client.get(f"/vessel/{vessel_id}/inspections/{detail_id}", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return TypesInspectionDetailResponse.model_validate(r.json())

    async def ownership(self, vessel_id: str, *, filter_id_type: str = "imo") -> TypesOwnershipResponse:
        """Retrieve ownership data for a vessel."""
        r = await self._client.get(f"/vessel/{vessel_id}/ownership", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return TypesOwnershipResponse.model_validate(r.json())

    async def positions(self, *, filter_id_type: str = "imo", filter_ids: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselPositionsResponse:
        """Retrieve positions for multiple vessels."""
        r = await self._client.get("/vessels/positions", params=_strip_none({"filter.idType": filter_id_type, "filter.ids": filter_ids, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselPositionsResponse.model_validate(r.json())

    # --- Iterators ---

    def all_casualties(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None) -> AsyncIterator[MarineCasualty]:
        """Iterate over all casualties for a vessel across pages."""
        token: str | None = None
        async def fetch() -> tuple[list[MarineCasualty], str | None]:
            nonlocal token
            resp = await self.casualties(vessel_id, filter_id_type=filter_id_type, pagination_limit=pagination_limit, pagination_next_token=token)
            token = resp.next_token
            return resp.casualties or [], token
        return AsyncIterator(fetch)

    def all_emissions(self, vessel_id: str, *, filter_id_type: str = "imo", pagination_limit: int | None = None) -> AsyncIterator[VesselEmission]:
        """Iterate over all emissions for a vessel across pages."""
        token: str | None = None
        async def fetch() -> tuple[list[VesselEmission], str | None]:
            nonlocal token
            resp = await self.emissions(vessel_id, filter_id_type=filter_id_type, pagination_limit=pagination_limit, pagination_next_token=token)
            token = resp.next_token
            return resp.emissions or [], token
        return AsyncIterator(fetch)

    def all_positions(self, *, filter_id_type: str = "imo", filter_ids: str | None = None, pagination_limit: int | None = None) -> AsyncIterator[VesselPosition]:
        """Iterate over all positions for multiple vessels across pages."""
        token: str | None = None
        async def fetch() -> tuple[list[VesselPosition], str | None]:
            nonlocal token
            resp = await self.positions(filter_id_type=filter_id_type, filter_ids=filter_ids, pagination_limit=pagination_limit, pagination_next_token=token)
            token = resp.next_token
            return resp.vessel_positions or [], token
        return AsyncIterator(fetch)


class AsyncPortsService:
    """Port lookup endpoints (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get(self, unlocode: str) -> PortResponse:
        """Retrieve a port by its UN/LOCODE."""
        r = await self._client.get(f"/port/{unlocode}")
        error_from_response(r.status_code, r.content)
        return PortResponse.model_validate(r.json())

    async def inbound(self, unlocode: str, *, eta_from: str, eta_to: str, time_from: str | None = None, time_to: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortInboundResponse:
        """Retrieve vessels heading to a port."""
        r = await self._client.get(f"/port/{unlocode}/inbound", params=_strip_none({"filter.etaFrom": eta_from, "filter.etaTo": eta_to, "time.from": time_from, "time.to": time_to, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortInboundResponse.model_validate(r.json())

    def inbound_all(self, unlocode: str, *, eta_from: str, eta_to: str, time_from: str | None = None, time_to: str | None = None, pagination_limit: int | None = None) -> AsyncIterator[VesselETA]:
        """Iterate over all inbound vessels for a port across pages."""
        token: str | None = None
        async def fetch() -> tuple[list[VesselETA], str | None]:
            nonlocal token
            resp = await self.inbound(unlocode, eta_from=eta_from, eta_to=eta_to, time_from=time_from, time_to=time_to, pagination_limit=pagination_limit, pagination_next_token=token)
            token = resp.next_token
            return resp.vessel_etas or [], token
        return AsyncIterator(fetch)


class AsyncPortEventsService:
    """Port event endpoints (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def list(self, *, time_from: str | None = None, time_to: str | None = None, filter_country: str | None = None, filter_unlocode: str | None = None, filter_event_type: str | None = None, filter_vessel_name: str | None = None, filter_port_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events with optional filtering."""
        r = await self._client.get("/portevents", params=_strip_none({"time.from": time_from, "time.to": time_to, "filter.country": filter_country, "filter.unlocode": filter_unlocode, "filter.eventType": filter_event_type, "filter.vesselName": filter_vessel_name, "filter.portName": filter_port_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    async def by_port(self, unlocode: str, *, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events for a specific port by UNLOCODE."""
        r = await self._client.get(f"/portevents/port/{unlocode}", params=_strip_none({"pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    async def by_ports(self, *, filter_port_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events by port name search."""
        r = await self._client.get("/portevents/ports", params=_strip_none({"filter.portName": filter_port_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    async def by_vessel(self, vessel_id: str, *, filter_id_type: str = "imo", filter_event_type: str | None = None, filter_sort_order: str | None = None, time_from: str | None = None, time_to: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events for a specific vessel."""
        r = await self._client.get(f"/portevents/vessel/{vessel_id}", params=_strip_none({"filter.idType": filter_id_type, "filter.eventType": filter_event_type, "filter.sortOrder": filter_sort_order, "time.from": time_from, "time.to": time_to, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    async def last_by_vessel(self, vessel_id: str, *, filter_id_type: str = "imo") -> PortEventResponse:
        """Retrieve the last port event for a vessel."""
        r = await self._client.get(f"/portevents/vessel/{vessel_id}/last", params=_strip_none({"filter.idType": filter_id_type}))
        error_from_response(r.status_code, r.content)
        return PortEventResponse.model_validate(r.json())

    async def by_vessels(self, *, filter_vessel_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortEventsResponse:
        """Retrieve port events by vessel name search."""
        r = await self._client.get("/portevents/vessels", params=_strip_none({"filter.vesselName": filter_vessel_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortEventsResponse.model_validate(r.json())

    # --- Iterators ---

    def list_all(self, **kwargs: Any) -> AsyncIterator[PortEvent]:
        """Iterate over all port events across pages."""
        token: str | None = None
        async def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = await self.list(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return AsyncIterator(fetch)

    def all_by_port(self, unlocode: str, **kwargs: Any) -> AsyncIterator[PortEvent]:
        """Iterate over all port events for a specific port."""
        token: str | None = None
        async def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = await self.by_port(unlocode, **kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return AsyncIterator(fetch)

    def all_by_ports(self, **kwargs: Any) -> AsyncIterator[PortEvent]:
        """Iterate over all port events by port name search."""
        token: str | None = None
        async def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = await self.by_ports(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return AsyncIterator(fetch)

    def all_by_vessel(self, vessel_id: str, **kwargs: Any) -> AsyncIterator[PortEvent]:
        """Iterate over all port events for a vessel."""
        token: str | None = None
        async def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = await self.by_vessel(vessel_id, **kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return AsyncIterator(fetch)

    def all_by_vessels(self, **kwargs: Any) -> AsyncIterator[PortEvent]:
        """Iterate over all port events by vessel name search."""
        token: str | None = None
        async def fetch() -> tuple[list[PortEvent], str | None]:
            nonlocal token
            resp = await self.by_vessels(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.port_events or [], token
        return AsyncIterator(fetch)


class AsyncEmissionsService:
    """Emissions endpoints (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def list(self, *, filter_period: int | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselEmissionsResponse:
        """Retrieve vessel emissions data."""
        r = await self._client.get("/emissions", params=_strip_none({"filter.period": filter_period, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselEmissionsResponse.model_validate(r.json())

    def list_all(self, **kwargs: Any) -> AsyncIterator[VesselEmission]:
        """Iterate over all emissions across pages."""
        token: str | None = None
        async def fetch() -> tuple[list[VesselEmission], str | None]:
            nonlocal token
            resp = await self.list(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.emissions or [], token
        return AsyncIterator(fetch)


class AsyncSearchService:
    """Search endpoints (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def vessels(self, *, filter_name: str | None = None, filter_imo: str | None = None, filter_mmsi: str | None = None, filter_flag: str | None = None, filter_vessel_type: str | None = None, filter_callsign: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindVesselsResponse:
        """Search for vessels."""
        r = await self._client.get("/search/vessels", params=_strip_none({"filter.name": filter_name, "filter.imo": filter_imo, "filter.mmsi": filter_mmsi, "filter.flag": filter_flag, "filter.vesselType": filter_vessel_type, "filter.callsign": filter_callsign, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindVesselsResponse.model_validate(r.json())

    async def ports(self, *, filter_name: str | None = None, filter_country: str | None = None, filter_port_type: str | None = None, filter_region: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindPortsResponse:
        """Search for ports."""
        r = await self._client.get("/search/ports", params=_strip_none({"filter.name": filter_name, "filter.country": filter_country, "filter.type": filter_port_type, "filter.region": filter_region, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindPortsResponse.model_validate(r.json())

    async def dgps(self, *, filter_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindDGPSStationsResponse:
        """Search for DGPS stations."""
        r = await self._client.get("/search/dgps", params=_strip_none({"filter.name": filter_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindDGPSStationsResponse.model_validate(r.json())

    async def light_aids(self, *, filter_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindLightAidsResponse:
        """Search for light aids."""
        r = await self._client.get("/search/lightaids", params=_strip_none({"filter.name": filter_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindLightAidsResponse.model_validate(r.json())

    async def modus(self, *, filter_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindMODUsResponse:
        """Search for MODUs."""
        r = await self._client.get("/search/modus", params=_strip_none({"filter.name": filter_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindMODUsResponse.model_validate(r.json())

    async def radio_beacons(self, *, filter_name: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> FindRadioBeaconsResponse:
        """Search for radio beacons."""
        r = await self._client.get("/search/radiobeacons", params=_strip_none({"filter.name": filter_name, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return FindRadioBeaconsResponse.model_validate(r.json())

    # --- Iterators ---

    def all_vessels(self, **kwargs: Any) -> AsyncIterator[Vessel]:
        """Iterate over all vessel search results."""
        token: str | None = None
        async def fetch() -> tuple[list[Vessel], str | None]:
            nonlocal token
            resp = await self.vessels(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.vessels or [], token
        return AsyncIterator(fetch)

    def all_ports(self, **kwargs: Any) -> AsyncIterator[Port]:
        """Iterate over all port search results."""
        token: str | None = None
        async def fetch() -> tuple[list[Port], str | None]:
            nonlocal token
            resp = await self.ports(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.ports or [], token
        return AsyncIterator(fetch)

    def all_dgps(self, **kwargs: Any) -> AsyncIterator[DGPSStation]:
        """Iterate over all DGPS station search results."""
        token: str | None = None
        async def fetch() -> tuple[list[DGPSStation], str | None]:
            nonlocal token
            resp = await self.dgps(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.dgps_stations or [], token
        return AsyncIterator(fetch)

    def all_light_aids(self, **kwargs: Any) -> AsyncIterator[LightAid]:
        """Iterate over all light aid search results."""
        token: str | None = None
        async def fetch() -> tuple[list[LightAid], str | None]:
            nonlocal token
            resp = await self.light_aids(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.light_aids or [], token
        return AsyncIterator(fetch)

    def all_modus(self, **kwargs: Any) -> AsyncIterator[MODU]:
        """Iterate over all MODU search results."""
        token: str | None = None
        async def fetch() -> tuple[list[MODU], str | None]:
            nonlocal token
            resp = await self.modus(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.modus or [], token
        return AsyncIterator(fetch)

    def all_radio_beacons(self, **kwargs: Any) -> AsyncIterator[RadioBeacon]:
        """Iterate over all radio beacon search results."""
        token: str | None = None
        async def fetch() -> tuple[list[RadioBeacon], str | None]:
            nonlocal token
            resp = await self.radio_beacons(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.radio_beacons or [], token
        return AsyncIterator(fetch)


class AsyncLocationService:
    """Location-based query endpoints (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def vessels_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselsWithinLocationResponse:
        """Retrieve vessel positions within a bounding box."""
        r = await self._client.get("/location/vessels/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselsWithinLocationResponse.model_validate(r.json())

    async def vessels_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> VesselsWithinLocationResponse:
        """Retrieve vessel positions within a radius."""
        r = await self._client.get("/location/vessels/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return VesselsWithinLocationResponse.model_validate(r.json())

    async def ports_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortsWithinLocationResponse:
        """Retrieve ports within a bounding box."""
        r = await self._client.get("/location/ports/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortsWithinLocationResponse.model_validate(r.json())

    async def ports_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> PortsWithinLocationResponse:
        """Retrieve ports within a radius."""
        r = await self._client.get("/location/ports/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return PortsWithinLocationResponse.model_validate(r.json())

    async def dgps_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> DGPSStationsWithinLocationResponse:
        """Retrieve DGPS stations within a bounding box."""
        r = await self._client.get("/location/dgps/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return DGPSStationsWithinLocationResponse.model_validate(r.json())

    async def dgps_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> DGPSStationsWithinLocationResponse:
        """Retrieve DGPS stations within a radius."""
        r = await self._client.get("/location/dgps/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return DGPSStationsWithinLocationResponse.model_validate(r.json())

    async def light_aids_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> LightAidsWithinLocationResponse:
        """Retrieve light aids within a bounding box."""
        r = await self._client.get("/location/lightaids/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return LightAidsWithinLocationResponse.model_validate(r.json())

    async def light_aids_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> LightAidsWithinLocationResponse:
        """Retrieve light aids within a radius."""
        r = await self._client.get("/location/lightaids/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return LightAidsWithinLocationResponse.model_validate(r.json())

    async def modus_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> MODUsWithinLocationResponse:
        """Retrieve MODUs within a bounding box."""
        r = await self._client.get("/location/modu/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return MODUsWithinLocationResponse.model_validate(r.json())

    async def modus_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> MODUsWithinLocationResponse:
        """Retrieve MODUs within a radius."""
        r = await self._client.get("/location/modu/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return MODUsWithinLocationResponse.model_validate(r.json())

    async def radio_beacons_bounding_box(self, *, lat_min: float | None = None, lat_max: float | None = None, lon_min: float | None = None, lon_max: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> RadioBeaconsWithinLocationResponse:
        """Retrieve radio beacons within a bounding box."""
        r = await self._client.get("/location/radiobeacons/bounding-box", params=_strip_none({"filter.latBottom": lat_min, "filter.latTop": lat_max, "filter.lonLeft": lon_min, "filter.lonRight": lon_max, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return RadioBeaconsWithinLocationResponse.model_validate(r.json())

    async def radio_beacons_radius(self, *, latitude: float | None = None, longitude: float | None = None, radius: float | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> RadioBeaconsWithinLocationResponse:
        """Retrieve radio beacons within a radius."""
        r = await self._client.get("/location/radiobeacons/radius", params=_strip_none({"filter.latitude": latitude, "filter.longitude": longitude, "filter.radius": radius, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return RadioBeaconsWithinLocationResponse.model_validate(r.json())

    # --- Iterators ---

    def all_vessels_bounding_box(self, **kwargs: Any) -> AsyncIterator[VesselPosition]:
        """Iterate over all vessel positions in a bounding box."""
        token: str | None = None
        async def fetch() -> tuple[list[VesselPosition], str | None]:
            nonlocal token
            resp = await self.vessels_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.vessels or [], token
        return AsyncIterator(fetch)

    def all_vessels_radius(self, **kwargs: Any) -> AsyncIterator[VesselPosition]:
        """Iterate over all vessel positions within a radius."""
        token: str | None = None
        async def fetch() -> tuple[list[VesselPosition], str | None]:
            nonlocal token
            resp = await self.vessels_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.vessels or [], token
        return AsyncIterator(fetch)

    def all_ports_bounding_box(self, **kwargs: Any) -> AsyncIterator[Port]:
        """Iterate over all ports in a bounding box."""
        token: str | None = None
        async def fetch() -> tuple[list[Port], str | None]:
            nonlocal token
            resp = await self.ports_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.ports or [], token
        return AsyncIterator(fetch)

    def all_ports_radius(self, **kwargs: Any) -> AsyncIterator[Port]:
        """Iterate over all ports within a radius."""
        token: str | None = None
        async def fetch() -> tuple[list[Port], str | None]:
            nonlocal token
            resp = await self.ports_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.ports or [], token
        return AsyncIterator(fetch)

    def all_dgps_bounding_box(self, **kwargs: Any) -> AsyncIterator[DGPSStation]:
        """Iterate over all DGPS stations in a bounding box."""
        token: str | None = None
        async def fetch() -> tuple[list[DGPSStation], str | None]:
            nonlocal token
            resp = await self.dgps_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.dgps_stations or [], token
        return AsyncIterator(fetch)

    def all_dgps_radius(self, **kwargs: Any) -> AsyncIterator[DGPSStation]:
        """Iterate over all DGPS stations within a radius."""
        token: str | None = None
        async def fetch() -> tuple[list[DGPSStation], str | None]:
            nonlocal token
            resp = await self.dgps_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.dgps_stations or [], token
        return AsyncIterator(fetch)

    def all_light_aids_bounding_box(self, **kwargs: Any) -> AsyncIterator[LightAid]:
        """Iterate over all light aids in a bounding box."""
        token: str | None = None
        async def fetch() -> tuple[list[LightAid], str | None]:
            nonlocal token
            resp = await self.light_aids_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.light_aids or [], token
        return AsyncIterator(fetch)

    def all_light_aids_radius(self, **kwargs: Any) -> AsyncIterator[LightAid]:
        """Iterate over all light aids within a radius."""
        token: str | None = None
        async def fetch() -> tuple[list[LightAid], str | None]:
            nonlocal token
            resp = await self.light_aids_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.light_aids or [], token
        return AsyncIterator(fetch)

    def all_modus_bounding_box(self, **kwargs: Any) -> AsyncIterator[MODU]:
        """Iterate over all MODUs in a bounding box."""
        token: str | None = None
        async def fetch() -> tuple[list[MODU], str | None]:
            nonlocal token
            resp = await self.modus_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.modus or [], token
        return AsyncIterator(fetch)

    def all_modus_radius(self, **kwargs: Any) -> AsyncIterator[MODU]:
        """Iterate over all MODUs within a radius."""
        token: str | None = None
        async def fetch() -> tuple[list[MODU], str | None]:
            nonlocal token
            resp = await self.modus_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.modus or [], token
        return AsyncIterator(fetch)

    def all_radio_beacons_bounding_box(self, **kwargs: Any) -> AsyncIterator[RadioBeacon]:
        """Iterate over all radio beacons in a bounding box."""
        token: str | None = None
        async def fetch() -> tuple[list[RadioBeacon], str | None]:
            nonlocal token
            resp = await self.radio_beacons_bounding_box(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.radio_beacons or [], token
        return AsyncIterator(fetch)

    def all_radio_beacons_radius(self, **kwargs: Any) -> AsyncIterator[RadioBeacon]:
        """Iterate over all radio beacons within a radius."""
        token: str | None = None
        async def fetch() -> tuple[list[RadioBeacon], str | None]:
            nonlocal token
            resp = await self.radio_beacons_radius(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.radio_beacons or [], token
        return AsyncIterator(fetch)


class AsyncNavtexService:
    """NAVTEX message endpoints (async)."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def list(self, *, time_from: str | None = None, time_to: str | None = None, pagination_limit: int | None = None, pagination_next_token: str | None = None) -> NavtexMessagesResponse:
        """Retrieve NAVTEX maritime safety messages."""
        r = await self._client.get("/navtex", params=_strip_none({"time.from": time_from, "time.to": time_to, "pagination.limit": pagination_limit, "pagination.nextToken": pagination_next_token}))
        error_from_response(r.status_code, r.content)
        return NavtexMessagesResponse.model_validate(r.json())

    def list_all(self, **kwargs: Any) -> AsyncIterator[Navtex]:
        """Iterate over all NAVTEX messages across pages."""
        token: str | None = None
        async def fetch() -> tuple[list[Navtex], str | None]:
            nonlocal token
            resp = await self.list(**kwargs, pagination_next_token=token)
            token = resp.next_token
            return resp.navtex_messages or [], token
        return AsyncIterator(fetch)
