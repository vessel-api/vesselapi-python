"""Pydantic v2 models for the Vessel Tracking API.

Models follow Python conventions. They are maintained by hand — there is no code
generator — but they now cover every property of every response definition in
openapi/swagger.json. Error payloads are the one deliberate exception: they are
surfaced as exceptions in ``_errors`` rather than as models here.

Because pydantic silently drops unmodelled keys, a property added to the spec
must be added here too or callers lose the data with no error. When the spec
changes, diff it against these classes.

All optional fields use ``type | None = None`` and JSON field mapping uses
``Field(alias="camelCase")`` where the API returns camelCase keys. Note that
``Vessel`` is snake_case on the wire and so needs no aliases.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Base config shared by all models
# ---------------------------------------------------------------------------


class _Base(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Shared / helper sub-models
# ---------------------------------------------------------------------------


class GeoJSON(_Base):
    """GeoJSON Point geometry for geospatial coordinates."""

    coordinates: list[float] | None = None
    type: str | None = None


class PortCountry(_Base):
    """Country information for a port."""

    code: str | None = None
    name: str | None = None


class PortReference(_Base):
    """Port identification details used in port event references."""

    country: str | None = None
    name: str | None = None
    unlo_code: str | None = None


class VesselReference(_Base):
    """Vessel identification details used in port event references."""

    imo: int | None = None
    mmsi: int | None = None
    name: str | None = None


class VesselFormerName(_Base):
    """Historical vessel name record."""

    name: str | None = None
    year_until: str | None = None


class ResolutionMeta(_Base):
    """Metadata about ID resolution fallback. Present when the API resolved using a different ID type."""

    requested_id_type: str | None = Field(default=None, alias="requestedIdType")
    resolved_id_type: str | None = Field(default=None, alias="resolvedIdType")
    resolved_id: int | None = Field(default=None, alias="resolvedId")
    suggested_id_type: str | None = Field(default=None, alias="suggestedIdType")


# ---------------------------------------------------------------------------
# Vessel models
# ---------------------------------------------------------------------------


class Vessel(_Base):
    """A vessel record with complete static data."""

    breadth: int | None = None
    breadth_unit: str | None = None
    call_sign: str | None = None
    country: str | None = None
    country_code: str | None = None
    deadweight_tonnage: int | None = None
    draft: int | None = None
    draft_unit: str | None = None
    draught_calculated_avg: float | None = None
    draught_observed_max: float | None = None
    engine_model_name: str | None = None
    engine_type: int | None = None
    eni: str | None = None
    former_names: list[VesselFormerName] | None = None
    gross_tonnage: int | None = None
    home_port: str | None = None
    imo: int | None = None
    kilowatt_power: int | None = None
    length: int | None = None
    length_unit: str | None = None
    mmsi: int | None = None
    name: str | None = None
    name_ais: str | None = None
    operating_status: str | None = None
    speed_calculated_avg: float | None = None
    speed_observed_max: float | None = None
    summer_draught: float | None = None
    teu: int | None = None
    vessel_subtype: str | None = None
    vessel_type: str | None = None
    year_built: int | None = None


class VesselResponse(_Base):
    """Response for a single vessel lookup."""

    vessel: Vessel | None = None
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class VesselPosition(_Base):
    """A real-time vessel position record from AIS data."""

    cog: float | None = None
    heading: int | None = None
    imo: int | None = None
    latitude: float | None = None
    location: GeoJSON | None = None
    longitude: float | None = None
    mmsi: int | None = None
    nav_status: int | None = None
    processed_timestamp: str | None = None
    sog: float | None = None
    suspected_glitch: bool | None = None
    timestamp: str | None = None
    vessel_name: str | None = None


class VesselPositionResponse(_Base):
    """Response for a single vessel position lookup."""

    vessel_position: VesselPosition | None = Field(default=None, alias="vesselPosition")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class VesselPositionsResponse(_Base):
    """Response for multiple vessel positions."""

    vessel_positions: list[VesselPosition] | None = Field(default=None, alias="vesselPositions")
    next_token: str | None = Field(default=None, alias="nextToken")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


# ---------------------------------------------------------------------------
# Vessel sub-resource models
# ---------------------------------------------------------------------------


class MarineCasualty(_Base):
    """A marine casualty record."""

    at_coding: list[str] | None = Field(default=None, alias="atCoding")
    casualty_report_nr: str | None = Field(default=None, alias="casualtyReportNr")
    cf_coding: list[str] | None = Field(default=None, alias="cfCoding")
    collected_at: str | None = Field(default=None, alias="collectedAt")
    competent_authority: list[str] | None = Field(default=None, alias="competentAuthority")
    date_of_occurrence: str | None = Field(default=None, alias="dateOfOccurrence")
    deviation: list[str] | None = None
    event_type: list[str] | None = Field(default=None, alias="eventType")
    finished_investigation: bool | None = Field(default=None, alias="finishedInvestigation")
    imo_nr: list[str] | None = Field(default=None, alias="imoNr")
    interim_report: bool | None = Field(default=None, alias="interimReport")
    investigating_state: str | None = Field(default=None, alias="investigatingState")
    lives_lost_total: str | None = Field(default=None, alias="livesLostTotal")
    name_of_ship: list[str] | None = Field(default=None, alias="nameOfShip")
    occurrence_severity: str | None = Field(default=None, alias="occurrenceSeverity")
    occurrence_uuid: str | None = Field(default=None, alias="occurrenceUuid")
    occurrence_with_persons: list[str] | None = Field(default=None, alias="occurrenceWithPersons")
    occurrence_with_ships: list[str] | None = Field(default=None, alias="occurrenceWithShips")
    people_injured_total: str | None = Field(default=None, alias="peopleInjuredTotal")
    pollution: bool | None = None
    ship_craft_type: list[str] | None = Field(default=None, alias="shipCraftType")
    sr_coding: list[str] | None = Field(default=None, alias="srCoding")


class MarineCasualtiesResponse(_Base):
    """Response for vessel casualties."""

    casualties: list[MarineCasualty] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class VesselEmission(_Base):
    """A vessel emission record (EU MRV data)."""

    co2_emissions_at_berth: float | None = None
    co2_emissions_on_laden_voyages: float | None = None
    co2_emissions_total: float | None = None
    co2_per_distance: float | None = None
    co2_per_transport_work: float | None = None
    collected_at: str | None = None
    distance_through_ice: float | None = None
    doc_expiry_date: str | None = None
    doc_issue_date: str | None = None
    flag_code: str | None = None
    flag_name: str | None = None
    fuel_consumption_hfo: float | None = None
    fuel_consumption_lfo: float | None = None
    fuel_consumption_lng: float | None = None
    fuel_consumption_mdo: float | None = None
    fuel_consumption_mgo: float | None = None
    fuel_consumption_other: float | None = None
    fuel_consumption_total: float | None = None
    fuel_per_distance: float | None = None
    fuel_per_transport_work: float | None = None
    home_port: str | None = None
    ice_class: str | None = None
    imo: int | None = None
    monitoring_method_a: str | None = None
    monitoring_method_b: str | None = None
    monitoring_method_c: str | None = None
    monitoring_method_d: str | None = None
    name: str | None = None
    port_calls_outside_eu: int | None = None
    port_calls_within_eu: int | None = None
    reporting_period: str | None = None
    source_url: str | None = None
    technical_efficiency: str | None = None
    technical_efficiency_value: float | None = None
    time_at_sea_through_ice: float | None = None
    total_time_at_sea: float | None = None
    unique_key: str | None = None
    verifier_accreditation: str | None = None
    verifier_address: str | None = None
    verifier_name: str | None = None
    vessel_type: str | None = None


class VesselEmissionsResponse(_Base):
    """Response for vessel emissions."""

    emissions: list[VesselEmission] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class VesselETA(_Base):
    """Vessel Estimated Time of Arrival information."""

    destination: str | None = None
    destination_port: str | None = None
    draught: float | None = None
    eta: str | None = None
    imo: int | None = None
    mmsi: int | None = None
    timestamp: str | None = None
    vessel_name: str | None = None


class VesselETAResponse(_Base):
    """Response for vessel ETA."""

    vessel_eta: VesselETA | None = Field(default=None, alias="vesselEta")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class PortInboundResponse(_Base):
    """Response containing vessels heading to a port."""

    vessel_etas: list[VesselETA] | None = Field(default=None, alias="vesselETAs")
    next_token: str | None = Field(default=None, alias="nextToken")


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


class Port(_Base):
    """A port record with complete harbor details and facilities."""

    anchorage_depth: float | None = None
    anchorage_depth_unit: str | None = None
    cargo_handling_depth: float | None = None
    cargo_handling_depth_unit: str | None = None
    channel_depth: float | None = None
    channel_depth_unit: str | None = None
    country: PortCountry | None = None
    garbage_disposal: bool | None = None
    harbor_size: str | None = None
    harbor_type: str | None = None
    harbor_use: str | None = None
    has_drydock: bool | None = None
    latitude: float | None = None
    location: GeoJSON | None = None
    longitude: float | None = None
    max_vessel_beam: float | None = None
    max_vessel_beam_unit: str | None = None
    max_vessel_draft: float | None = None
    max_vessel_draft_unit: str | None = None
    max_vessel_length: float | None = None
    max_vessel_length_unit: str | None = None
    medical_facilities: bool | None = None
    name: str | None = None
    navigation_area: str | None = None
    pilotage_available: bool | None = None
    pilotage_compulsory: bool | None = None
    port_security: bool | None = None
    region_name: str | None = None
    repair_capability: str | None = None
    shelter: str | None = None
    size: str | None = None
    supply_diesel: bool | None = None
    supply_fuel: bool | None = None
    supply_water: bool | None = None
    traffic_separation_scheme: bool | None = None
    tugs_available: bool | None = None
    type: str | None = None
    unlo_code: str | None = None
    vessel_traffic_service: bool | None = None


class PortResponse(_Base):
    """Response for a single port lookup."""

    port: Port | None = None


# ---------------------------------------------------------------------------
# Port event models
# ---------------------------------------------------------------------------


class PortEvent(_Base):
    """A port event (arrival/departure) record."""

    event: str | None = None
    port: PortReference | None = None
    timestamp: str | None = None
    vessel: VesselReference | None = None


class PortEventsResponse(_Base):
    """Response for port events list."""

    port_events: list[PortEvent] | None = Field(default=None, alias="portEvents")
    next_token: str | None = Field(default=None, alias="nextToken")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class PortEventResponse(_Base):
    """Response for a single port event (e.g. last by vessel)."""

    port_event: PortEvent | None = Field(default=None, alias="portEvent")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


# ---------------------------------------------------------------------------
# Search models
# ---------------------------------------------------------------------------


class VesselSearchMeta(_Base):
    """Metadata about which fields matched a vessel search query.

    ``matched_on`` maps the index of a vessel in the ``vessels`` array to the
    fields that matched it, e.g. ``{"0": ["eni"], "1": ["imo"]}``. Values are
    arrays because one vessel can match on several fields at once.
    """

    matched_on: dict[str, list[str]] | None = Field(default=None, alias="matchedOn")
    query: str | None = None


class FindVesselsResponse(_Base):
    """Response for vessel search."""

    vessels: list[Vessel] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")
    meta: VesselSearchMeta | None = Field(default=None, alias="_meta")


class FindPortsResponse(_Base):
    """Response for port search."""

    ports: list[Port] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")


class DGPSStation(_Base):
    """A DGPS station record."""

    aid_type: str | None = None
    delete_flag: str | None = None
    feature_number: float | None = None
    frequency: float | None = None
    geopolitical_heading: str | None = None
    location: GeoJSON | None = None
    name: str | None = None
    notice_number: int | None = None
    notice_week: str | None = None
    notice_year: str | None = None
    position: str | None = None
    post_note: str | None = None
    preceding_note: str | None = None
    range: int | None = None
    region_heading: str | None = None
    remarks: str | None = None
    remove_from_list: str | None = None
    station_id: str | None = None
    transfer_rate: int | None = None
    volume_number: str | None = None


class FindDGPSStationsResponse(_Base):
    """Response for DGPS station search."""

    dgps_stations: list[DGPSStation] | None = Field(default=None, alias="dgpsStations")
    next_token: str | None = Field(default=None, alias="nextToken")


class LightAid(_Base):
    """A light aid to navigation record."""

    aid_type: str | None = None
    characteristic: str | None = None
    characteristic_number: int | None = None
    delete_flag: str | None = None
    feature_number: str | None = None
    geopolitical_heading: str | None = None
    height_feet_meters: str | None = None
    local_heading: str | None = None
    location: GeoJSON | None = None
    name: str | None = None
    notice_number: int | None = None
    notice_week: str | None = None
    notice_year: str | None = None
    position: str | None = None
    post_note: str | None = None
    preceding_note: str | None = None
    range: str | None = None
    region_heading: str | None = None
    remarks: str | None = None
    remove_from_list: str | None = None
    structure: str | None = None
    subregion_heading: str | None = None
    volume_number: str | None = None


class FindLightAidsResponse(_Base):
    """Response for light aids search."""

    light_aids: list[LightAid] | None = Field(default=None, alias="lightAids")
    next_token: str | None = Field(default=None, alias="nextToken")


class MODU(_Base):
    """A Mobile Offshore Drilling Unit record."""

    date: str | None = None
    distance: float | None = None
    latitude: float | None = None
    location: GeoJSON | None = None
    longitude: float | None = None
    name: str | None = None
    navigation_area: str | None = None
    position: str | None = None
    region: int | None = None
    rig_status: str | None = None
    special_status: str | None = None
    sub_region: int | None = None


class FindMODUsResponse(_Base):
    """Response for MODU search."""

    modus: list[MODU] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")


class RadioBeacon(_Base):
    """A radio beacon record."""

    aid_type: str | None = None
    characteristic: str | None = None
    delete_flag: str | None = None
    feature_number: float | None = None
    frequency: str | None = None
    geopolitical_heading: str | None = None
    location: GeoJSON | None = None
    name: str | None = None
    notice_number: int | None = None
    notice_week: str | None = None
    notice_year: str | None = None
    position: str | None = None
    post_note: str | None = None
    preceding_note: str | None = None
    range: str | None = None
    region_heading: str | None = None
    remove_from_list: str | None = None
    sequence_text: str | None = None
    station_remark: str | None = None
    volume_number: str | None = None


class FindRadioBeaconsResponse(_Base):
    """Response for radio beacon search."""

    radio_beacons: list[RadioBeacon] | None = Field(default=None, alias="radioBeacons")
    next_token: str | None = Field(default=None, alias="nextToken")


# ---------------------------------------------------------------------------
# Location query response models
# ---------------------------------------------------------------------------


class VesselsWithinLocationResponse(_Base):
    """Response for vessel location queries (bounding box or radius)."""

    vessels: list[VesselPosition] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")


class PortsWithinLocationResponse(_Base):
    """Response for port location queries."""

    ports: list[Port] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")


class DGPSStationsWithinLocationResponse(_Base):
    """Response for DGPS station location queries."""

    dgps_stations: list[DGPSStation] | None = Field(default=None, alias="dgpsStations")
    next_token: str | None = Field(default=None, alias="nextToken")


class LightAidsWithinLocationResponse(_Base):
    """Response for light aids location queries."""

    light_aids: list[LightAid] | None = Field(default=None, alias="lightAids")
    next_token: str | None = Field(default=None, alias="nextToken")


class MODUsWithinLocationResponse(_Base):
    """Response for MODU location queries."""

    modus: list[MODU] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")


class RadioBeaconsWithinLocationResponse(_Base):
    """Response for radio beacon location queries."""

    radio_beacons: list[RadioBeacon] | None = Field(default=None, alias="radioBeacons")
    next_token: str | None = Field(default=None, alias="nextToken")


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
