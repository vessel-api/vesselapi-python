"""Pydantic v2 models for the Vessel Tracking API.

Models are generated from the OpenAPI spec and follow Python conventions.
All optional fields use ``type | None = None`` and JSON field mapping uses
``Field(alias="camelCase")`` where the API returns camelCase keys.
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


class BroadcastStation(_Base):
    """NAVTEX radio broadcast station details."""

    country: str | None = None
    coverage: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    name: str | None = None
    station_id: str | None = None


# ---------------------------------------------------------------------------
# Classification sub-models
# ---------------------------------------------------------------------------


class ClassificationPurpose(_Base):
    """Purpose entry within classification identification."""

    description: str | None = None
    is_main_purpose: bool | None = Field(default=None, alias="isMainPurpose")
    purpose: str | None = None


class ClassificationCertificate(_Base):
    """Certificate entry within vessel classification."""

    certificate: str | None = None
    code: str | None = None
    expires: str | None = None
    ext_until: str | None = Field(default=None, alias="extUntil")
    issued: str | None = None
    term: str | None = None
    type: str | None = None


class ClassificationCondition(_Base):
    """Condition entry within vessel classification."""

    condition: str | None = None
    due_date: str | None = Field(default=None, alias="dueDate")
    imposed_date: str | None = Field(default=None, alias="imposedDate")


class ClassificationDimensions(_Base):
    """Vessel dimensions from classification data."""

    bm: float | None = None
    dm: float | None = None
    draught: float | None = None
    dwt: float | None = None
    gross_ton_69: float | None = Field(default=None, alias="grossTon69")
    lbp: float | None = None
    length_overall: float | None = Field(default=None, alias="lengthOverall")
    net_ton_69: float | None = Field(default=None, alias="netTon69")


class ClassificationHull(_Base):
    """Hull details from classification data."""

    decks_number: str | None = Field(default=None, alias="decksNumber")


class ClassificationIdentification(_Base):
    """Identification details from classification data."""

    class_status_string: str | None = Field(default=None, alias="classStatusString")
    flag_code: str | None = Field(default=None, alias="flagCode")
    flag_name: str | None = Field(default=None, alias="flagName")
    home_port: str | None = Field(default=None, alias="homePort")
    imo_number: str | None = Field(default=None, alias="imoNumber")
    non_class_relation_string: str | None = Field(
        default=None, alias="nonClassRelationString"
    )
    official_number: str | None = Field(default=None, alias="officialNumber")
    operational_status_string: str | None = Field(
        default=None, alias="operationalStatusString"
    )
    purposes: list[ClassificationPurpose] | None = None
    register_: str | None = Field(default=None, alias="register")
    signal_letters: str | None = Field(default=None, alias="signalLetters")
    type_formatted: str | None = Field(default=None, alias="typeFormatted")
    vessel_id: str | None = Field(default=None, alias="vesselId")
    vessel_name: str | None = Field(default=None, alias="vesselName")


class ClassificationInfo(_Base):
    """Classification notation and class status details."""

    class_entry_date: str | None = Field(default=None, alias="classEntryDate")
    class_notation_string: str | None = Field(
        default=None, alias="classNotationString"
    )
    class_notation_string_design: str | None = Field(
        default=None, alias="classNotationStringDesign"
    )
    class_notation_string_in_operation: str | None = Field(
        default=None, alias="classNotationStringInOperation"
    )
    class_notation_string_main: str | None = Field(
        default=None, alias="classNotationStringMain"
    )
    construction_symbol: str | None = Field(default=None, alias="constructionSymbol")
    dual_class: str | None = Field(default=None, alias="dualClass")
    equipment_number: str | None = Field(default=None, alias="equipmentNumber")
    last_classification_society: str | None = Field(
        default=None, alias="lastClassificationSociety"
    )
    main_class: str | None = Field(default=None, alias="mainClass")
    main_class_machinery: str | None = Field(
        default=None, alias="mainClassMachinery"
    )
    register_notation_string: str | None = Field(
        default=None, alias="registerNotationString"
    )


class ClassificationMachinery(_Base):
    """Machinery details from classification data."""

    main_propulsion: str | None = Field(default=None, alias="mainPropulsion")


class ClassificationOwner(_Base):
    """Owner/manager details from classification data."""

    doc_holder_dnv_id: str | None = Field(default=None, alias="docHolderDnvId")
    doc_holder_imo_number: str | None = Field(
        default=None, alias="docHolderImoNumber"
    )
    doc_holder_name: str | None = Field(default=None, alias="docHolderName")
    manager_dnv_id: str | None = Field(default=None, alias="managerDnvId")
    manager_imo_number: str | None = Field(default=None, alias="managerImoNumber")
    manager_name: str | None = Field(default=None, alias="managerName")
    owner_dnv_id: str | None = Field(default=None, alias="ownerDnvId")
    owner_imo_number: str | None = Field(default=None, alias="ownerImoNumber")
    owner_name: str | None = Field(default=None, alias="ownerName")


class ClassificationSurvey(_Base):
    """Survey entry within vessel classification."""

    category: str | None = None
    due_from: str | None = Field(default=None, alias="dueFrom")
    due_to: str | None = Field(default=None, alias="dueTo")
    last_date: str | None = Field(default=None, alias="lastDate")
    location: str | None = None
    postponed: str | None = None
    survey: str | None = None


class ClassificationYard(_Base):
    """Shipyard/builder details from classification data."""

    contracted_builder: str | None = Field(default=None, alias="contractedBuilder")
    contracted_builder_build_no: str | None = Field(
        default=None, alias="contractedBuilderBuildNo"
    )
    date_of_build: str | None = Field(default=None, alias="dateOfBuild")
    hull_yard_build_no: str | None = Field(default=None, alias="hullYardBuildNo")
    hull_yard_name: str | None = Field(default=None, alias="hullYardName")
    keel_date: str | None = Field(default=None, alias="keelDate")


# ---------------------------------------------------------------------------
# Resolution metadata
# ---------------------------------------------------------------------------


class ResolutionMeta(_Base):
    """Metadata about ID resolution fallback. Present when the API resolved using a different ID type."""
    requested_id_type: str | None = Field(default=None, alias="requestedIdType")
    resolved_id_type: str | None = Field(default=None, alias="resolvedIdType")
    resolved_id: int | None = Field(default=None, alias="resolvedId")


# ---------------------------------------------------------------------------
# Vessel models
# ---------------------------------------------------------------------------


class Vessel(_Base):
    """A vessel record with complete static data."""

    breadth: int | None = None
    breadth_unit: str | None = None
    builder: str | None = None
    call_sign: str | None = None
    class_society: str | None = None
    country: str | None = None
    country_code: str | None = None
    deadweight_tonnage: int | None = None
    draft: int | None = None
    draft_unit: str | None = None
    engine_model_name: str | None = None
    engine_type: int | None = None
    former_names: list[VesselFormerName] | None = None
    gross_tonnage: int | None = None
    home_port: str | None = None
    imo: int | None = None
    kilowatt_power: int | None = None
    length: int | None = None
    length_unit: str | None = None
    manager_name: str | None = None
    mmsi: int | None = None
    name: str | None = None
    operating_status: str | None = None
    owner_name: str | None = None
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

    vessel_position: VesselPosition | None = Field(
        default=None, alias="vesselPosition"
    )
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class VesselPositionsResponse(_Base):
    """Response for multiple vessel positions."""

    vessel_positions: list[VesselPosition] | None = Field(
        default=None, alias="vesselPositions"
    )
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
    competent_authority: list[str] | None = Field(
        default=None, alias="competentAuthority"
    )
    date_of_occurrence: str | None = Field(default=None, alias="dateOfOccurrence")
    deviation: list[str] | None = None
    event_type: list[str] | None = Field(default=None, alias="eventType")
    finished_investigation: bool | None = Field(
        default=None, alias="finishedInvestigation"
    )
    imo_nr: list[str] | None = Field(default=None, alias="imoNr")
    interim_report: bool | None = Field(default=None, alias="interimReport")
    investigating_state: str | None = Field(
        default=None, alias="investigatingState"
    )
    lives_lost_total: str | None = Field(default=None, alias="livesLostTotal")
    name_of_ship: list[str] | None = Field(default=None, alias="nameOfShip")
    occurrence_severity: str | None = Field(
        default=None, alias="occurrenceSeverity"
    )
    occurrence_uuid: str | None = Field(default=None, alias="occurrenceUuid")
    occurrence_with_persons: list[str] | None = Field(
        default=None, alias="occurrenceWithPersons"
    )
    occurrence_with_ships: list[str] | None = Field(
        default=None, alias="occurrenceWithShips"
    )
    people_injured_total: str | None = Field(
        default=None, alias="peopleInjuredTotal"
    )
    pollution: bool | None = None
    ship_craft_type: list[str] | None = Field(default=None, alias="shipCraftType")
    sr_coding: list[str] | None = Field(default=None, alias="srCoding")


class MarineCasualtiesResponse(_Base):
    """Response for vessel casualties."""

    casualties: list[MarineCasualty] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class ClassificationVessel(_Base):
    """Full vessel classification data with nested sub-objects."""

    certificates: list[ClassificationCertificate] | None = None
    classification: ClassificationInfo | None = None
    collected_at: str | None = Field(default=None, alias="collectedAt")
    conditions: list[ClassificationCondition] | None = None
    dimensions: ClassificationDimensions | None = None
    hull: ClassificationHull | None = None
    identification: ClassificationIdentification | None = None
    imo: int | None = None
    machinery: ClassificationMachinery | None = None
    owner: ClassificationOwner | None = None
    surveys: list[ClassificationSurvey] | None = None
    yard: ClassificationYard | None = None


# Keep the ``Classification`` alias so existing code continues to work.
Classification = ClassificationVessel


class ClassificationResponse(_Base):
    """Response for vessel classification."""

    classification: ClassificationVessel | None = None
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
# Inspection models
# ---------------------------------------------------------------------------


class InspectionRecord(_Base):
    """A port-state control inspection record (from types.Inspection)."""

    authority: str | None = None
    deficiencies: int | None = None
    detail_id: str | None = None
    detained: bool | None = None
    imo: int | None = None
    inspection_date: str | None = None
    inspection_type: str | None = None
    mou_region: str | None = None
    port: str | None = None


# Keep ``Inspection`` as an alias so existing imports keep working.
Inspection = InspectionRecord


class InspectionDeficiency(_Base):
    """A deficiency entry from an inspection detail."""

    category: str | None = None
    count: int | None = None
    deficiency: str | None = None


class InspectionDetailRecord(_Base):
    """Detailed inspection record with deficiency breakdown."""

    authority: str | None = None
    deficiencies: list[InspectionDeficiency] | None = None
    deficiency_count: int | None = None
    detail_id: str | None = None
    detained: bool | None = None
    detention_grounds: list[InspectionDeficiency] | None = None
    imo: int | None = None
    inspection_date: str | None = None
    inspection_type: str | None = None
    mou_region: str | None = None
    port: str | None = None


# Keep ``InspectionDetail`` as an alias so existing imports keep working.
InspectionDetail = InspectionDetailRecord


class InspectionsResponseData(_Base):
    """Inner data of the inspections response (types.InspectionsResponse)."""

    cached_at: str | None = None
    imo: int | None = None
    inspection_count: int | None = None
    inspections: list[InspectionRecord] | None = None


class TypesInspectionsResponse(_Base):
    """Response for vessel inspections (wraps InspectionsResponseData)."""

    cached_at: str | None = None
    imo: int | None = None
    inspection_count: int | None = None
    inspections: list[InspectionRecord] | None = None


class InspectionDetailResponseData(_Base):
    """Inner data of the inspection detail response."""

    cached_at: str | None = None
    detail_id: str | None = None
    imo: int | None = None
    inspection_detail: InspectionDetailRecord | None = None


class TypesInspectionDetailResponse(_Base):
    """Response for a detailed inspection."""

    cached_at: str | None = None
    detail_id: str | None = None
    imo: int | None = None
    inspection_detail: InspectionDetailRecord | None = None


# ---------------------------------------------------------------------------
# Ownership models
# ---------------------------------------------------------------------------


class VesselOwnership(_Base):
    """Vessel ownership and management details."""

    doc_company: str | None = None
    doc_company_address: str | None = None
    imo: int | None = None
    registered_owner: str | None = None
    registered_owner_address: str | None = None
    ship_manager: str | None = None
    ship_manager_address: str | None = None


# Keep ``Ownership`` as an alias so existing imports keep working.
Ownership = VesselOwnership


class OwnershipResponseData(_Base):
    """Inner data of the ownership response (types.OwnershipResponse)."""

    cached_at: str | None = None
    imo: int | None = None
    ownership: VesselOwnership | None = None


class TypesOwnershipResponse(_Base):
    """Response for vessel ownership."""

    cached_at: str | None = None
    imo: int | None = None
    ownership: VesselOwnership | None = None


# ---------------------------------------------------------------------------
# Port models
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

    port_events: list[PortEvent] | None = Field(
        default=None, alias="portEvents"
    )
    next_token: str | None = Field(default=None, alias="nextToken")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


class PortEventResponse(_Base):
    """Response for a single port event (e.g. last by vessel)."""

    port_event: PortEvent | None = Field(default=None, alias="portEvent")
    meta: ResolutionMeta | None = Field(default=None, alias="_meta")


# ---------------------------------------------------------------------------
# Search models
# ---------------------------------------------------------------------------


class FindVesselsResponse(_Base):
    """Response for vessel search."""

    vessels: list[Vessel] | None = None
    next_token: str | None = Field(default=None, alias="nextToken")


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

    dgps_stations: list[DGPSStation] | None = Field(
        default=None, alias="dgpsStations"
    )
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

    radio_beacons: list[RadioBeacon] | None = Field(
        default=None, alias="radioBeacons"
    )
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

    dgps_stations: list[DGPSStation] | None = Field(
        default=None, alias="dgpsStations"
    )
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

    radio_beacons: list[RadioBeacon] | None = Field(
        default=None, alias="radioBeacons"
    )
    next_token: str | None = Field(default=None, alias="nextToken")


# ---------------------------------------------------------------------------
# Navtex models
# ---------------------------------------------------------------------------


class Navtex(_Base):
    """A NAVTEX maritime safety message."""

    issuing_office: str | None = None
    label: str | None = None
    lines: list[str] | None = None
    metarea_coordinator: str | None = None
    metarea_id: str | None = None
    metarea_name: str | None = None
    metarea_region: str | None = None
    metarea_stations: list[BroadcastStation] | None = None
    raw_content: str | None = None
    timestamp: str | None = None
    wmo_header: str | None = None


class NavtexMessagesResponse(_Base):
    """Response for NAVTEX messages list."""

    navtex_messages: list[Navtex] | None = Field(
        default=None, alias="navtexMessages"
    )
    next_token: str | None = Field(default=None, alias="nextToken")
