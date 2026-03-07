"""Tests for service methods."""

from __future__ import annotations

import httpx
import pytest
import respx

from vessel_api_python import VesselClient, VesselNotFoundError


class TestVesselsService:
    """Tests for the VesselsService."""

    def test_get_vessel(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessel/9363728").mock(
                return_value=httpx.Response(200, json={"vessel": {"imo": 9363728, "name": "Ever Given"}})
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.vessels.get("9363728")
            assert result.vessel is not None
            assert result.vessel.imo == 9363728
            assert result.vessel.name == "Ever Given"
            # Verify filter.idType=imo is sent by default.
            assert "filter.idType=imo" in str(route.calls[0].request.url)
            client.close()

    def test_get_vessel_not_found(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/vessel/0000000").mock(
                return_value=httpx.Response(404, json={"error": {"message": "Vessel not found"}})
            )
            client = VesselClient(api_key="key", max_retries=0)
            with pytest.raises(VesselNotFoundError):
                client.vessels.get("0000000")
            client.close()

    def test_position(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/vessel/9363728/position").mock(
                return_value=httpx.Response(200, json={"vesselPosition": {"imo": 9363728, "latitude": 55.0}})
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.vessels.position("9363728")
            assert result.vessel_position is not None
            assert result.vessel_position.latitude == 55.0
            client.close()


class TestPortsService:
    """Tests for the PortsService."""

    def test_get_port(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/port/NLRTM").mock(
                return_value=httpx.Response(200, json={"port": {"name": "Rotterdam", "unloCode": "NLRTM"}})
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.ports.get("NLRTM")
            assert result.port is not None
            assert result.port.name == "Rotterdam"
            client.close()

    def test_inbound(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/port/NLRTM/inbound").mock(
                return_value=httpx.Response(200, json={
                    "vesselETAs": [
                        {"imo": 9363728, "vessel_name": "Ever Given", "eta": "2026-03-10T12:00:00Z", "destination_port": "NLRTM"},
                    ],
                    "nextToken": None,
                })
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.ports.inbound("NLRTM", eta_from="2026-03-07T00:00:00Z", eta_to="2026-03-14T00:00:00Z")
            assert result.vessel_etas is not None
            assert len(result.vessel_etas) == 1
            assert result.vessel_etas[0].imo == 9363728
            assert result.vessel_etas[0].vessel_name == "Ever Given"
            # Verify filter params are sent.
            url = str(route.calls[0].request.url)
            assert "filter.etaFrom=2026-03-07" in url
            assert "filter.etaTo=2026-03-14" in url
            client.close()


class TestResolutionMeta:
    """Tests for _meta deserialization on response models."""

    def test_meta_on_vessel_response(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/vessel/477045900").mock(
                return_value=httpx.Response(200, json={
                    "vessel": {"imo": 9363728, "mmsi": 477045900},
                    "_meta": {"requestedIdType": "imo", "resolvedIdType": "mmsi", "resolvedId": 477045900},
                })
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.vessels.get("477045900", filter_id_type="imo")
            assert result.meta is not None
            assert result.meta.requested_id_type == "imo"
            assert result.meta.resolved_id_type == "mmsi"
            assert result.meta.resolved_id == 477045900
            client.close()

    def test_meta_absent_when_no_fallback(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/vessel/9363728").mock(
                return_value=httpx.Response(200, json={"vessel": {"imo": 9363728}})
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.vessels.get("9363728")
            assert result.meta is None
            client.close()


class TestSearchService:
    """Tests for the SearchService."""

    def test_search_vessels(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={
                    "vessels": [{"imo": 9363728, "name": "Ever Given"}],
                    "nextToken": None,
                })
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.search.vessels(filter_name="Ever Given")
            assert result.vessels is not None
            assert len(result.vessels) == 1
            assert result.vessels[0].name == "Ever Given"
            client.close()

    def test_search_ports(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/search/ports").mock(
                return_value=httpx.Response(200, json={
                    "ports": [{"name": "Rotterdam", "unloCode": "NLRTM"}],
                    "nextToken": None,
                })
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.search.ports(filter_country="NL")
            assert result.ports is not None
            assert len(result.ports) == 1
            client.close()


class TestPortEventsService:
    """Tests for the PortEventsService."""

    def test_list_port_events(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/portevents").mock(
                return_value=httpx.Response(200, json={
                    "portEvents": [{"event": "arrival", "portName": "Rotterdam"}],
                    "nextToken": None,
                })
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.port_events.list()
            assert result.port_events is not None
            assert len(result.port_events) == 1
            assert result.port_events[0].event == "arrival"
            client.close()

    def test_by_vessel_defaults_to_imo(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/portevents/vessel/9363728").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.port_events.by_vessel("9363728")
            assert "filter.idType=imo" in str(route.calls[0].request.url)
            client.close()
