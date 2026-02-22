"""Smoke tests that hit the live Vessel API.

Run with:
    VESSELAPI_API_KEY=<key> pytest -m smoke -v

All tests are skipped when VESSELAPI_API_KEY is not set.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest

from vessel_api_python import VesselClient
from vessel_api_python._errors import VesselAPIError

pytestmark = pytest.mark.smoke

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("VESSELAPI_API_KEY", "")
BASE_URL = os.environ.get("VESSELAPI_BASE_URL", "https://api.vesselapi.com/v1")


@pytest.fixture(scope="module")
def client() -> VesselClient:
    if not API_KEY:
        pytest.skip("VESSELAPI_API_KEY not set")
    return VesselClient(api_key=API_KEY, base_url=BASE_URL, max_retries=1)


def _require_api_error(exc_info: pytest.ExceptionInfo[VesselAPIError], status: int) -> None:
    assert exc_info.value.status_code == status


# ---------------------------------------------------------------------------
# Vessels (10 subtests)
# ---------------------------------------------------------------------------


class TestSmoke_Vessels:
    def test_get(self, client: VesselClient) -> None:
        resp = client.vessels.get("9321483")
        assert resp.vessel is not None
        assert resp.vessel.imo is not None and resp.vessel.imo != 0

    def test_position(self, client: VesselClient) -> None:
        resp = client.vessels.position("232003239", filter_id_type="mmsi")
        assert resp.vessel_position is not None

    def test_casualties(self, client: VesselClient) -> None:
        resp = client.vessels.casualties("9321483")
        assert resp is not None

    def test_classification(self, client: VesselClient) -> None:
        resp = client.vessels.classification("9121998")
        assert resp.classification is not None

    def test_emissions(self, client: VesselClient) -> None:
        resp = client.vessels.emissions("1045356")
        assert resp is not None

    def test_eta(self, client: VesselClient) -> None:
        resp = client.vessels.eta("232003239", filter_id_type="mmsi")
        assert resp is not None

    def test_inspections(self, client: VesselClient) -> None:
        resp = client.vessels.inspections("9121998")
        assert resp is not None
        if resp.inspection_count is not None and resp.inspection_count == 0:
            pytest.skip("no inspections returned")

    def test_inspection_detail(self, client: VesselClient) -> None:
        insp_resp = client.vessels.inspections("9121998")
        if not insp_resp.inspections:
            pytest.skip("no inspections available to test detail endpoint")
        detail_id = insp_resp.inspections[0].detail_id
        if not detail_id:
            pytest.skip("first inspection has no detail_id")
        resp = client.vessels.inspection_detail("9121998", detail_id)
        assert resp is not None
        assert resp.detail_id == detail_id

    def test_ownership(self, client: VesselClient) -> None:
        resp = client.vessels.ownership("9121998")
        assert resp is not None

    def test_positions(self, client: VesselClient) -> None:
        resp = client.vessels.positions(filter_id_type="mmsi", filter_ids="232003239,246497000")
        assert resp is not None


# ---------------------------------------------------------------------------
# Ports (1 subtest)
# ---------------------------------------------------------------------------


class TestSmoke_Ports:
    def test_get(self, client: VesselClient) -> None:
        resp = client.ports.get("NLRTM")
        assert resp.port is not None
        assert resp.port.unlo_code == "NLRTM"


# ---------------------------------------------------------------------------
# PortEvents (9 subtests)
# ---------------------------------------------------------------------------


class TestSmoke_PortEvents:
    def test_list(self, client: VesselClient) -> None:
        now = datetime.now(timezone.utc)
        day_ago = (now - timedelta(hours=24)).isoformat()
        resp = client.port_events.list(time_from=day_ago, time_to=now.isoformat(), pagination_limit=5)
        assert resp is not None

    def test_list_filter_country(self, client: VesselClient) -> None:
        resp = client.port_events.list(filter_country="Singapore", pagination_limit=5)
        assert resp is not None

    def test_list_filter_event_type(self, client: VesselClient) -> None:
        resp = client.port_events.list(filter_event_type="arrival", pagination_limit=5)
        assert resp is not None

    def test_list_combined_filters(self, client: VesselClient) -> None:
        resp = client.port_events.list(filter_country="Singapore", filter_event_type="arrival", pagination_limit=5)
        assert resp is not None

    def test_by_port(self, client: VesselClient) -> None:
        resp = client.port_events.by_port("NLRTM", pagination_limit=5)
        assert resp is not None

    def test_by_ports(self, client: VesselClient) -> None:
        resp = client.port_events.by_ports(filter_port_name="Rotterdam", pagination_limit=5)
        assert resp is not None

    def test_by_vessel(self, client: VesselClient) -> None:
        resp = client.port_events.by_vessel("9863132", pagination_limit=5)
        assert resp is not None

    def test_last_by_vessel(self, client: VesselClient) -> None:
        resp = client.port_events.last_by_vessel("9863132")
        assert resp is not None

    def test_by_vessels(self, client: VesselClient) -> None:
        resp = client.port_events.by_vessels(filter_vessel_name="strangford 2", pagination_limit=5)
        assert resp is not None


# ---------------------------------------------------------------------------
# Emissions (1 subtest)
# ---------------------------------------------------------------------------


class TestSmoke_Emissions:
    def test_list(self, client: VesselClient) -> None:
        resp = client.emissions.list(filter_period=2024, pagination_limit=5)
        assert resp is not None
        assert resp.emissions is not None and len(resp.emissions) > 0


# ---------------------------------------------------------------------------
# Search (12 subtests)
# ---------------------------------------------------------------------------


class TestSmoke_Search:
    def test_vessels(self, client: VesselClient) -> None:
        resp = client.search.vessels(filter_name="EVER GIVEN")
        assert resp is not None
        assert resp.vessels is not None and len(resp.vessels) > 0

    def test_vessels_filter_flag(self, client: VesselClient) -> None:
        resp = client.search.vessels(filter_flag="PA", pagination_limit=5)
        assert resp is not None
        assert resp.vessels is not None and len(resp.vessels) > 0

    def test_vessels_filter_vessel_type(self, client: VesselClient) -> None:
        resp = client.search.vessels(filter_vessel_type="Container Ship", pagination_limit=5)
        assert resp is not None
        assert resp.vessels is not None and len(resp.vessels) > 0

    def test_vessels_combined_filters(self, client: VesselClient) -> None:
        resp = client.search.vessels(filter_flag="PA", filter_vessel_type="Container Ship", pagination_limit=5)
        assert resp is not None

    def test_ports(self, client: VesselClient) -> None:
        resp = client.search.ports(filter_name="Rotterdam")
        assert resp is not None
        assert resp.ports is not None and len(resp.ports) > 0

    def test_ports_filter_country(self, client: VesselClient) -> None:
        resp = client.search.ports(filter_country="NL", pagination_limit=5)
        assert resp is not None
        assert resp.ports is not None and len(resp.ports) > 0

    def test_ports_filter_type(self, client: VesselClient) -> None:
        resp = client.search.ports(filter_port_type="Port", pagination_limit=5)
        assert resp is not None
        assert resp.ports is not None and len(resp.ports) > 0

    def test_ports_combined_filters(self, client: VesselClient) -> None:
        resp = client.search.ports(filter_country="NL", pagination_limit=5)
        assert resp is not None

    def test_dgps(self, client: VesselClient) -> None:
        resp = client.search.dgps(filter_name="Hammer Odde")
        assert resp is not None
        assert resp.dgps_stations is not None and len(resp.dgps_stations) > 0

    def test_light_aids(self, client: VesselClient) -> None:
        resp = client.search.light_aids(filter_name="Creach")
        assert resp is not None
        assert resp.light_aids is not None and len(resp.light_aids) > 0

    def test_modus(self, client: VesselClient) -> None:
        resp = client.search.modus(filter_name="ABAN")
        assert resp is not None
        assert resp.modus is not None and len(resp.modus) > 0

    def test_radio_beacons(self, client: VesselClient) -> None:
        resp = client.search.radio_beacons(filter_name="Brighton")
        assert resp is not None
        assert resp.radio_beacons is not None and len(resp.radio_beacons) > 0


# ---------------------------------------------------------------------------
# Location (12 subtests)
# ---------------------------------------------------------------------------


class TestSmoke_Location:
    def test_vessels_bounding_box(self, client: VesselClient) -> None:
        resp = client.location.vessels_bounding_box(lon_min=4.0, lon_max=5.0, lat_min=51.0, lat_max=52.0, pagination_limit=5)
        assert resp is not None

    def test_vessels_radius(self, client: VesselClient) -> None:
        resp = client.location.vessels_radius(longitude=4.5, latitude=51.5, radius=100000, pagination_limit=5)
        assert resp is not None

    def test_ports_bounding_box(self, client: VesselClient) -> None:
        resp = client.location.ports_bounding_box(lon_min=4.0, lon_max=5.0, lat_min=51.0, lat_max=52.0, pagination_limit=5)
        assert resp is not None
        assert resp.ports is not None and len(resp.ports) > 0

    def test_ports_radius(self, client: VesselClient) -> None:
        resp = client.location.ports_radius(longitude=4.5, latitude=51.5, radius=100000, pagination_limit=5)
        assert resp is not None
        assert resp.ports is not None and len(resp.ports) > 0

    def test_dgps_bounding_box(self, client: VesselClient) -> None:
        resp = client.location.dgps_bounding_box(lon_min=7.0, lon_max=9.0, lat_min=55.0, lat_max=56.0, pagination_limit=5)
        assert resp is not None

    def test_dgps_radius(self, client: VesselClient) -> None:
        resp = client.location.dgps_radius(longitude=8.084, latitude=55.558, radius=10000, pagination_limit=5)
        assert resp is not None

    def test_light_aids_bounding_box(self, client: VesselClient) -> None:
        resp = client.location.light_aids_bounding_box(lon_min=4.0, lon_max=5.0, lat_min=51.0, lat_max=52.0, pagination_limit=5)
        assert resp is not None

    def test_light_aids_radius(self, client: VesselClient) -> None:
        resp = client.location.light_aids_radius(longitude=4.5, latitude=51.5, radius=100000, pagination_limit=5)
        assert resp is not None

    def test_modus_bounding_box(self, client: VesselClient) -> None:
        resp = client.location.modus_bounding_box(lon_min=-89.0, lon_max=-88.0, lat_min=28.0, lat_max=29.0, pagination_limit=5)
        assert resp is not None

    def test_modus_radius(self, client: VesselClient) -> None:
        resp = client.location.modus_radius(longitude=-88.5, latitude=28.2, radius=50000, pagination_limit=5)
        assert resp is not None

    def test_radio_beacons_bounding_box(self, client: VesselClient) -> None:
        resp = client.location.radio_beacons_bounding_box(lon_min=-1.0, lon_max=1.0, lat_min=50.0, lat_max=51.0, pagination_limit=5)
        assert resp is not None

    def test_radio_beacons_radius(self, client: VesselClient) -> None:
        resp = client.location.radio_beacons_radius(longitude=-0.1, latitude=50.8, radius=100000, pagination_limit=5)
        assert resp is not None


# ---------------------------------------------------------------------------
# Navtex (1 subtest)
# ---------------------------------------------------------------------------


class TestSmoke_Navtex:
    def test_list(self, client: VesselClient) -> None:
        now = datetime.now(timezone.utc)
        day_ago = (now - timedelta(hours=24)).isoformat()
        resp = client.navtex.list(time_from=day_ago, time_to=now.isoformat(), pagination_limit=5)
        assert resp is not None


# ===========================================================================
# Bad-param tests
# ===========================================================================


# ---------------------------------------------------------------------------
# Bad-param: Vessels
# ---------------------------------------------------------------------------


class TestSmoke_Vessels_BadParams:
    def test_get_not_found_imo(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.get("0000000")
        _require_api_error(exc_info, 404)

    def test_get_not_found_mmsi(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.get("000000000", filter_id_type="mmsi")
        _require_api_error(exc_info, 404)

    def test_position_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.position("000000000", filter_id_type="mmsi")
        _require_api_error(exc_info, 404)

    def test_eta_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.eta("0000000")
        _require_api_error(exc_info, 404)

    def test_classification_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.classification("0000000")
        _require_api_error(exc_info, 404)

    def test_ownership_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.ownership("0000000")
        _require_api_error(exc_info, 404)

    def test_inspections_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.inspections("0000000")
        _require_api_error(exc_info, 404)

    def test_inspection_detail_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.inspection_detail("0000000", "nonexistent")
        _require_api_error(exc_info, 404)

    def test_casualties_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.casualties("0000000")
        _require_api_error(exc_info, 404)

    def test_casualties_exists_but_empty(self, client: VesselClient) -> None:
        resp = client.vessels.casualties("9778791")
        assert resp.casualties is None or len(resp.casualties) == 0

    def test_emissions_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.vessels.emissions("0000000")
        _require_api_error(exc_info, 404)

    def test_emissions_exists_but_empty(self, client: VesselClient) -> None:
        resp = client.vessels.emissions("9363728")
        assert resp.emissions is None or len(resp.emissions) == 0


# ---------------------------------------------------------------------------
# Bad-param: Ports
# ---------------------------------------------------------------------------


class TestSmoke_Ports_BadParams:
    def test_get_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.ports.get("ZZZZZ")
        _require_api_error(exc_info, 404)


# ---------------------------------------------------------------------------
# Bad-param: PortEvents
# ---------------------------------------------------------------------------


class TestSmoke_PortEvents_BadParams:
    def test_list_malformed_time_from(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.list(time_from="not-a-date")
        _require_api_error(exc_info, 400)

    def test_list_inverted_time_range(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.list(time_from="2025-01-02T00:00:00Z", time_to="2025-01-01T00:00:00Z")
        _require_api_error(exc_info, 400)

    def test_list_pagination_limit_too_high(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.list(pagination_limit=999)
        _require_api_error(exc_info, 400)

    def test_list_pagination_limit_negative(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.list(pagination_limit=-1)
        _require_api_error(exc_info, 400)

    def test_by_port_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.by_port("ZZZZZ", pagination_limit=5)
        _require_api_error(exc_info, 404)

    def test_by_vessel_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.by_vessel("000000000", filter_id_type="mmsi", pagination_limit=5)
        _require_api_error(exc_info, 404)

    def test_by_vessel_exists_but_empty(self, client: VesselClient) -> None:
        resp = client.port_events.by_vessel("219836000", filter_id_type="mmsi", pagination_limit=5)
        assert resp.port_events is None or len(resp.port_events) == 0

    def test_last_by_vessel_not_found(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.last_by_vessel("000000000", filter_id_type="mmsi")
        _require_api_error(exc_info, 404)

    def test_by_ports_empty_name(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.by_ports(filter_port_name="")
        _require_api_error(exc_info, 400)

    def test_by_vessels_empty_name(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.port_events.by_vessels(filter_vessel_name="")
        _require_api_error(exc_info, 400)


# ---------------------------------------------------------------------------
# Bad-param: Emissions
# ---------------------------------------------------------------------------


class TestSmoke_Emissions_BadParams:
    def test_list_pagination_limit_too_high(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.emissions.list(pagination_limit=999)
        _require_api_error(exc_info, 400)


# ---------------------------------------------------------------------------
# Bad-param: Search
# ---------------------------------------------------------------------------


class TestSmoke_Search_BadParams:
    def test_vessels_no_filters(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.search.vessels()
        _require_api_error(exc_info, 400)

    def test_vessels_pagination_too_high(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.search.vessels(filter_name="EVER GIVEN", pagination_limit=999)
        _require_api_error(exc_info, 400)

    def test_ports_no_filters(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.search.ports()
        _require_api_error(exc_info, 400)

    def test_dgps_empty_name(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.search.dgps(filter_name="")
        _require_api_error(exc_info, 400)

    def test_light_aids_empty_name(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.search.light_aids(filter_name="")
        _require_api_error(exc_info, 400)

    def test_modus_empty_name(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.search.modus(filter_name="")
        _require_api_error(exc_info, 400)

    def test_radio_beacons_empty_name(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.search.radio_beacons(filter_name="")
        _require_api_error(exc_info, 400)


# ---------------------------------------------------------------------------
# Bad-param: Location
# ---------------------------------------------------------------------------


class TestSmoke_Location_BadParams:
    def test_vessels_radius_latitude_too_high(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.vessels_radius(longitude=4.5, latitude=91.0, radius=10000)
        _require_api_error(exc_info, 400)

    def test_vessels_radius_longitude_too_high(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.vessels_radius(longitude=181.0, latitude=51.5, radius=10000)
        _require_api_error(exc_info, 400)

    def test_vessels_radius_too_large(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.vessels_radius(longitude=4.5, latitude=51.5, radius=200000)
        _require_api_error(exc_info, 400)

    def test_vessels_radius_negative(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.vessels_radius(longitude=4.5, latitude=51.5, radius=-1)
        _require_api_error(exc_info, 400)

    def test_vessels_bounding_box_inverted_lat(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.vessels_bounding_box(lon_min=4.0, lon_max=5.0, lat_min=52.0, lat_max=51.0)
        _require_api_error(exc_info, 400)

    def test_vessels_bounding_box_pagination_too_high(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.vessels_bounding_box(lon_min=4.0, lon_max=5.0, lat_min=51.0, lat_max=52.0, pagination_limit=999)
        _require_api_error(exc_info, 400)

    def test_ports_radius_too_large(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.ports_radius(longitude=4.5, latitude=51.5, radius=200000)
        _require_api_error(exc_info, 400)

    def test_ports_bounding_box_inverted_lon(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.ports_bounding_box(lon_min=5.0, lon_max=4.0, lat_min=51.0, lat_max=52.0)
        _require_api_error(exc_info, 400)

    def test_dgps_radius_latitude_too_low(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.dgps_radius(longitude=8.0, latitude=-91.0, radius=10000)
        _require_api_error(exc_info, 400)

    def test_light_aids_radius_longitude_too_low(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.light_aids_radius(longitude=-181.0, latitude=51.5, radius=10000)
        _require_api_error(exc_info, 400)

    def test_modus_radius_too_large(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.modus_radius(longitude=-88.5, latitude=28.2, radius=200000)
        _require_api_error(exc_info, 400)

    def test_radio_beacons_radius_too_large(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.location.radio_beacons_radius(longitude=-0.1, latitude=50.8, radius=200000)
        _require_api_error(exc_info, 400)


# ---------------------------------------------------------------------------
# Bad-param: Navtex
# ---------------------------------------------------------------------------


class TestSmoke_Navtex_BadParams:
    def test_list_malformed_time_from(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.navtex.list(time_from="not-a-date")
        _require_api_error(exc_info, 400)

    def test_list_pagination_limit_negative(self, client: VesselClient) -> None:
        with pytest.raises(VesselAPIError) as exc_info:
            client.navtex.list(pagination_limit=-1)
        _require_api_error(exc_info, 400)
