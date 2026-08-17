"""Tests for service methods."""

from __future__ import annotations

import inspect

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
                return_value=httpx.Response(
                    200,
                    json={
                        "vesselETAs": [
                            {
                                "imo": 9363728,
                                "vessel_name": "Ever Given",
                                "eta": "2026-03-10T12:00:00Z",
                                "destination_port": "NLRTM",
                            },
                        ],
                        "nextToken": None,
                    },
                )
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
                return_value=httpx.Response(
                    200,
                    json={
                        "vessel": {"imo": 9363728, "mmsi": 477045900},
                        "_meta": {"requestedIdType": "imo", "resolvedIdType": "mmsi", "resolvedId": 477045900},
                    },
                )
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

    def test_suggested_id_type(self) -> None:
        """suggestedIdType is emitted on a total miss to hint at retrying with the other id."""
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/vessel/232003239").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "vessel": None,
                        "_meta": {"requestedIdType": "imo", "suggestedIdType": "mmsi"},
                    },
                )
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.vessels.get("232003239", filter_id_type="imo")
            assert result.meta is not None
            assert result.meta.suggested_id_type == "mmsi"
            client.close()


class TestVesselStaticFields:
    """Every Vessel property the spec declares must survive deserialization.

    Pydantic drops unmodelled keys silently, so a field missing from the model
    is invisible to the caller rather than an error. These wire keys are
    snake_case in the spec, so none of them carry an alias.
    """

    def test_identity_and_capacity_fields(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/vessel/9321483").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "vessel": {
                            "imo": 9321483,
                            "eni": "02320524",
                            "teu": 23992,
                            "vessel_type": "Container Ship",
                            "vessel_subtype": "Inland cargo",
                            "name": "EVER GIVEN",
                            "name_ais": "EVER GIVEN 2",
                        }
                    },
                )
            )
            client = VesselClient(api_key="key", max_retries=0)
            vessel = client.vessels.get("9321483").vessel
            assert vessel is not None
            assert vessel.eni == "02320524"
            assert vessel.teu == 23992
            assert vessel.vessel_subtype == "Inland cargo"
            assert vessel.name_ais == "EVER GIVEN 2"
            # The registered name must stay distinct from the AIS-broadcast one.
            assert vessel.name == "EVER GIVEN"
            client.close()

    def test_draught_and_speed_fields(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/vessel/9321483").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "vessel": {
                            "imo": 9321483,
                            "summer_draught": 16.5,
                            "draught_calculated_avg": 13.8,
                            "draught_observed_max": 16.0,
                            "speed_calculated_avg": 12.4,
                            "speed_observed_max": 22.1,
                        }
                    },
                )
            )
            client = VesselClient(api_key="key", max_retries=0)
            vessel = client.vessels.get("9321483").vessel
            assert vessel is not None
            assert vessel.summer_draught == 16.5
            assert vessel.draught_calculated_avg == 13.8
            assert vessel.draught_observed_max == 16.0
            assert vessel.speed_calculated_avg == 12.4
            assert vessel.speed_observed_max == 22.1
            client.close()


class TestSearchService:
    """Tests for the SearchService."""

    def test_search_vessels(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "vessels": [{"imo": 9363728, "name": "Ever Given"}],
                        "nextToken": None,
                    },
                )
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.search.vessels(filter_name="Ever Given")
            assert result.vessels is not None
            assert len(result.vessels) == 1
            assert result.vessels[0].name == "Ever Given"
            client.close()

    def test_search_vessels_meta(self) -> None:
        """A q search returns _meta naming the fields each hit matched on."""
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "vessels": [{"eni": "4606770"}, {"imo": 4606770}],
                        "nextToken": None,
                        "_meta": {"matchedOn": {"0": ["eni"], "1": ["imo"]}, "query": "4606770"},
                    },
                )
            )
            client = VesselClient(api_key="key", max_retries=0)
            result = client.search.vessels(q="4606770")
            assert result.meta is not None
            assert result.meta.query == "4606770"
            assert result.meta.matched_on == {"0": ["eni"], "1": ["imo"]}
            assert "q=4606770" in str(route.calls[0].request.url)
            client.close()

    def test_search_vessels_meta_absent(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "vessels": [{"imo": 9363728}],
                        "nextToken": None,
                    },
                )
            )
            client = VesselClient(api_key="key", max_retries=0)
            assert client.search.vessels(filter_name="Ever Given").meta is None
            client.close()

    def test_search_vessels_filter_eni(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.search.vessels(filter_eni="02320524")
            assert "filter.eni=02320524" in str(route.calls[0].request.url)
            client.close()

    def test_search_ports(self) -> None:
        with respx.mock() as mock:
            mock.get("https://api.vesselapi.com/v1/search/ports").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "ports": [{"name": "Rotterdam", "unloCode": "NLRTM"}],
                        "nextToken": None,
                    },
                )
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
                return_value=httpx.Response(
                    200,
                    json={
                        "portEvents": [{"event": "arrival", "portName": "Rotterdam"}],
                        "nextToken": None,
                    },
                )
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


class TestIteratorParamForwarding:
    """Iterators must forward every param their signature accepts.

    all_positions previously accepted no time bounds at all while positions()
    supported them, so a time-bounded iteration silently returned the unbounded
    stream. These assert the params reach the wire, in both variants.
    """

    def test_all_positions_forwards_time_bounds(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessels/positions").mock(
                return_value=httpx.Response(200, json={"vesselPositions": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            list(
                client.vessels.all_positions(
                    filter_ids="232003239",
                    time_from="2026-08-01T00:00:00Z",
                    time_to="2026-08-02T00:00:00Z",
                )
            )
            url = str(route.calls[0].request.url)
            assert "time.from=2026-08-01T00%3A00%3A00Z" in url or "time.from=2026-08-01T00:00:00Z" in url
            assert "time.to=2026-08-02T00%3A00%3A00Z" in url or "time.to=2026-08-02T00:00:00Z" in url
            client.close()

    @pytest.mark.asyncio
    async def test_async_all_positions_forwards_time_bounds(self) -> None:
        from vessel_api_python import AsyncVesselClient

        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessels/positions").mock(
                return_value=httpx.Response(200, json={"vesselPositions": [], "nextToken": None})
            )
            client = AsyncVesselClient(api_key="key", max_retries=0)
            async for _ in client.vessels.all_positions(
                filter_ids="232003239",
                time_from="2026-08-01T00:00:00Z",
                time_to="2026-08-02T00:00:00Z",
            ):
                pass
            url = str(route.calls[0].request.url)
            assert "time.from" in url and "time.to" in url
            await client.aclose()


def _iterator_methods() -> list[tuple[str, str, object]]:
    """Every iterator method on every service class, sync and async.

    Identified by return annotation, so it picks up new endpoints automatically.
    """
    from vessel_api_python import _services

    classes = [
        _services.VesselsService,
        _services.PortsService,
        _services.PortEventsService,
        _services.EmissionsService,
        _services.SearchService,
        _services.LocationService,
        _services.AsyncVesselsService,
        _services.AsyncPortsService,
        _services.AsyncPortEventsService,
        _services.AsyncEmissionsService,
        _services.AsyncSearchService,
        _services.AsyncLocationService,
    ]
    found = []
    for cls in classes:
        for name, fn in vars(cls).items():
            if name.startswith("_") or not callable(fn):
                continue
            ann = inspect.signature(fn).return_annotation
            if isinstance(ann, str) and ("SyncIterator[" in ann or "AsyncIterator[" in ann):
                found.append((cls.__name__, name, fn))
    return found


class TestIteratorSignaturesAreExplicit:
    """Iterators must declare their params, not swallow **kwargs.

    With **kwargs a typo'd keyword was accepted and silently dropped, mypy
    could not check any call, and passing pagination_next_token blew up with
    "got multiple values" on the first fetch because the iterator supplies it.
    """

    def test_no_iterator_accepts_var_keyword(self) -> None:
        offenders = [
            f"{cls_name}.{name}"
            for cls_name, name, fn in _iterator_methods()
            if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in inspect.signature(fn).parameters.values())
        ]
        assert offenders == []

    def test_no_iterator_exposes_pagination_next_token(self) -> None:
        """The iterator owns the token; exposing it would collide with the internal one."""
        offenders = [
            f"{cls_name}.{name}"
            for cls_name, name, fn in _iterator_methods()
            if "pagination_next_token" in inspect.signature(fn).parameters
        ]
        assert offenders == []

    def test_iterator_surface_is_fully_typed(self) -> None:
        """Guards the count so a new endpoint cannot quietly reintroduce **kwargs."""
        assert len(_iterator_methods()) == 56

    def test_mistyped_keyword_raises_type_error(self) -> None:
        """filter_flg is not filter_flag. Previously accepted and ignored."""
        client = VesselClient(api_key="key", max_retries=0)
        with pytest.raises(TypeError, match="filter_flg"):
            client.search.all_vessels(filter_flg="NL")  # type: ignore[call-arg]
        client.close()

    @pytest.mark.asyncio
    async def test_async_mistyped_keyword_raises_type_error(self) -> None:
        from vessel_api_python import AsyncVesselClient

        client = AsyncVesselClient(api_key="key", max_retries=0)
        with pytest.raises(TypeError, match="filter_flg"):
            client.search.all_vessels(filter_flg="NL")  # type: ignore[call-arg]
        await client.aclose()

    def test_pagination_next_token_is_rejected(self) -> None:
        """Used to raise "got multiple values" at first iteration; now rejected at the call."""
        client = VesselClient(api_key="key", max_retries=0)
        with pytest.raises(TypeError, match="pagination_next_token"):
            client.port_events.list_all(pagination_next_token="abc")  # type: ignore[call-arg]
        client.close()

    def test_converted_iterator_forwards_params_to_wire(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            list(client.search.all_vessels(filter_flag="NL", filter_year_built_min=2010, pagination_limit=50))
            url = str(route.calls[0].request.url)
            assert "filter.flag=NL" in url
            assert "filter.yearBuiltMin=2010" in url
            assert "pagination.limit=50" in url
            client.close()

    def test_converted_location_iterator_forwards_bounds(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/location/vessels/bounding-box").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            list(client.location.all_vessels_bounding_box(lat_min=51.0, lat_max=52.0, lon_min=3.0, lon_max=4.0))
            url = str(route.calls[0].request.url)
            assert "filter.latBottom=51.0" in url
            assert "filter.latTop=52.0" in url
            assert "filter.lonLeft=3.0" in url
            assert "filter.lonRight=4.0" in url
            client.close()

    @pytest.mark.asyncio
    async def test_async_converted_iterator_forwards_params_to_wire(self) -> None:
        from vessel_api_python import AsyncVesselClient

        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            client = AsyncVesselClient(api_key="key", max_retries=0)
            async for _ in client.search.all_vessels(filter_flag="NL", filter_year_built_min=2010):
                pass
            url = str(route.calls[0].request.url)
            assert "filter.flag=NL" in url
            assert "filter.yearBuiltMin=2010" in url
            await client.aclose()


def _params(route: respx.Route) -> httpx.QueryParams:
    """Decoded query params of the first request a route captured."""
    return route.calls[0].request.url.params


class TestParamsAddedFromSpec:
    """Query params the spec declares that the client did not previously send.

    A param missing from the signature is unreachable: the caller cannot ask for
    satellite fallback or bound a port-event window, and gets the server default
    with no way to tell.
    """

    def test_position_sends_filter_sat(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessel/9363728/position").mock(
                return_value=httpx.Response(200, json={"vesselPosition": {"imo": 9363728}})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.vessels.position("9363728", filter_sat=True)
            assert _params(route).get("filter.sat") == "true"
            client.close()

    def test_position_omits_filter_sat_when_unset(self) -> None:
        """Unset must stay off the wire so the server default applies."""
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessel/9363728/position").mock(
                return_value=httpx.Response(200, json={"vesselPosition": {"imo": 9363728}})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.vessels.position("9363728")
            assert "filter.sat" not in _params(route)
            client.close()

    @pytest.mark.asyncio
    async def test_async_position_sends_filter_sat(self) -> None:
        from vessel_api_python import AsyncVesselClient

        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessel/9363728/position").mock(
                return_value=httpx.Response(200, json={"vesselPosition": {"imo": 9363728}})
            )
            client = AsyncVesselClient(api_key="key", max_retries=0)
            await client.vessels.position("9363728", filter_sat=False)
            assert _params(route).get("filter.sat") == "false"
            await client.aclose()

    def test_by_port_sends_time_bounds(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/portevents/port/NLRTM").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.port_events.by_port("NLRTM", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z")
            assert _params(route).get("time.from") == "2026-08-01T00:00:00Z"
            assert _params(route).get("time.to") == "2026-08-02T00:00:00Z"
            client.close()

    def test_by_ports_sends_time_bounds(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/portevents/ports").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.port_events.by_ports(
                filter_port_name="Rotterdam", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
            )
            params = _params(route)
            assert params.get("filter.portName") == "Rotterdam"
            assert params.get("time.from") == "2026-08-01T00:00:00Z"
            assert params.get("time.to") == "2026-08-02T00:00:00Z"
            client.close()

    def test_by_vessels_sends_time_bounds(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/portevents/vessels").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.port_events.by_vessels(
                filter_vessel_name="Ever Given", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
            )
            params = _params(route)
            assert params.get("filter.vesselName") == "Ever Given"
            assert params.get("time.from") == "2026-08-01T00:00:00Z"
            assert params.get("time.to") == "2026-08-02T00:00:00Z"
            client.close()

    @pytest.mark.asyncio
    async def test_async_portevents_time_bounds(self) -> None:
        from vessel_api_python import AsyncVesselClient

        with respx.mock() as mock:
            by_port = mock.get("https://api.vesselapi.com/v1/portevents/port/NLRTM").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            by_ports = mock.get("https://api.vesselapi.com/v1/portevents/ports").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            by_vessels = mock.get("https://api.vesselapi.com/v1/portevents/vessels").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            client = AsyncVesselClient(api_key="key", max_retries=0)
            await client.port_events.by_port("NLRTM", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z")
            await client.port_events.by_ports(
                filter_port_name="R", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
            )
            await client.port_events.by_vessels(
                filter_vessel_name="V", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
            )
            for route in (by_port, by_ports, by_vessels):
                assert _params(route).get("time.from") == "2026-08-01T00:00:00Z"
                assert _params(route).get("time.to") == "2026-08-02T00:00:00Z"
            await client.aclose()

    def test_portevents_iterators_forward_time_bounds(self) -> None:
        """The iterator is the usual way to read a window, so it must forward it too."""
        with respx.mock() as mock:
            by_port = mock.get("https://api.vesselapi.com/v1/portevents/port/NLRTM").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            by_ports = mock.get("https://api.vesselapi.com/v1/portevents/ports").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            by_vessels = mock.get("https://api.vesselapi.com/v1/portevents/vessels").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            list(
                client.port_events.all_by_port(
                    "NLRTM", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
                )
            )
            list(
                client.port_events.all_by_ports(
                    filter_port_name="R", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
                )
            )
            list(
                client.port_events.all_by_vessels(
                    filter_vessel_name="V", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
                )
            )
            for route in (by_port, by_ports, by_vessels):
                assert _params(route).get("time.from") == "2026-08-01T00:00:00Z"
                assert _params(route).get("time.to") == "2026-08-02T00:00:00Z"
            client.close()

    @pytest.mark.asyncio
    async def test_async_portevents_iterators_forward_time_bounds(self) -> None:
        from vessel_api_python import AsyncVesselClient

        with respx.mock() as mock:
            by_port = mock.get("https://api.vesselapi.com/v1/portevents/port/NLRTM").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            by_ports = mock.get("https://api.vesselapi.com/v1/portevents/ports").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            by_vessels = mock.get("https://api.vesselapi.com/v1/portevents/vessels").mock(
                return_value=httpx.Response(200, json={"portEvents": [], "nextToken": None})
            )
            client = AsyncVesselClient(api_key="key", max_retries=0)
            async for _ in client.port_events.all_by_port(
                "NLRTM", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
            ):
                pass
            async for _ in client.port_events.all_by_ports(
                filter_port_name="R", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
            ):
                pass
            async for _ in client.port_events.all_by_vessels(
                filter_vessel_name="V", time_from="2026-08-01T00:00:00Z", time_to="2026-08-02T00:00:00Z"
            ):
                pass
            for route in (by_port, by_ports, by_vessels):
                assert _params(route).get("time.from") == "2026-08-01T00:00:00Z"
                assert _params(route).get("time.to") == "2026-08-02T00:00:00Z"
            await client.aclose()


class TestMultiValueFilters:
    """Filters the spec marks "Repeat the parameter to match multiple".

    A list must go on the wire as a repeated param, never comma-joined, because
    the API treats a comma as part of a single value for these filters.
    """

    def test_flag_list_produces_repeated_params(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.search.vessels(filter_flag=["GB", "NO", "NL"])
            assert _params(route).get_list("filter.flag") == ["GB", "NO", "NL"]
            # Not comma-joined into one value.
            assert "filter.flag=GB%2CNO" not in str(route.calls[0].request.url)
            client.close()

    def test_single_string_still_produces_one_param(self) -> None:
        """The widened type must not change what existing string callers send."""
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.search.vessels(filter_flag="GB")
            assert _params(route).get_list("filter.flag") == ["GB"]
            client.close()

    def test_vessel_type_list(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.search.vessels(filter_vessel_type=["Container Ship", "Bulk Carrier"])
            assert _params(route).get_list("filter.vesselType") == ["Container Ship", "Bulk Carrier"]
            client.close()

    def test_search_ports_multi_filters(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/search/ports").mock(
                return_value=httpx.Response(200, json={"ports": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.search.ports(
                filter_country=["NL", "BE"],
                filter_port_type=["Seaport", "River"],
                filter_size=["Large", "Medium"],
                filter_harbor_size=["L", "M"],
                filter_harbor_use=["Commercial", "Fishing"],
            )
            params = _params(route)
            assert params.get_list("filter.country") == ["NL", "BE"]
            assert params.get_list("filter.type") == ["Seaport", "River"]
            assert params.get_list("filter.size") == ["Large", "Medium"]
            assert params.get_list("filter.harborSize") == ["L", "M"]
            assert params.get_list("filter.harborUse") == ["Commercial", "Fishing"]
            client.close()

    def test_positions_filter_ids_list(self) -> None:
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessels/positions").mock(
                return_value=httpx.Response(200, json={"vesselPositions": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.vessels.positions(filter_ids=["9363728", "9321483"])
            assert _params(route).get_list("filter.ids") == ["9363728", "9321483"]
            client.close()

    def test_positions_filter_ids_comma_string_unchanged(self) -> None:
        """The spec allows comma-separated in one param; that form must still pass through."""
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessels/positions").mock(
                return_value=httpx.Response(200, json={"vesselPositions": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.vessels.positions(filter_ids="9363728,9321483")
            assert _params(route).get_list("filter.ids") == ["9363728,9321483"]
            client.close()

    def test_iterators_forward_lists(self) -> None:
        with respx.mock() as mock:
            vessels = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            ports = mock.get("https://api.vesselapi.com/v1/search/ports").mock(
                return_value=httpx.Response(200, json={"ports": [], "nextToken": None})
            )
            positions = mock.get("https://api.vesselapi.com/v1/vessels/positions").mock(
                return_value=httpx.Response(200, json={"vesselPositions": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            list(client.search.all_vessels(filter_flag=["GB", "NO"]))
            list(client.search.all_ports(filter_country=["NL", "BE"]))
            list(client.vessels.all_positions(filter_ids=["9363728", "9321483"]))
            assert _params(vessels).get_list("filter.flag") == ["GB", "NO"]
            assert _params(ports).get_list("filter.country") == ["NL", "BE"]
            assert _params(positions).get_list("filter.ids") == ["9363728", "9321483"]
            client.close()

    @pytest.mark.asyncio
    async def test_async_lists_produce_repeated_params(self) -> None:
        from vessel_api_python import AsyncVesselClient

        with respx.mock() as mock:
            vessels = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            ports = mock.get("https://api.vesselapi.com/v1/search/ports").mock(
                return_value=httpx.Response(200, json={"ports": [], "nextToken": None})
            )
            positions = mock.get("https://api.vesselapi.com/v1/vessels/positions").mock(
                return_value=httpx.Response(200, json={"vesselPositions": [], "nextToken": None})
            )
            client = AsyncVesselClient(api_key="key", max_retries=0)
            await client.search.vessels(filter_flag=["GB", "NO"], filter_vessel_type=["Tug"])
            await client.search.ports(filter_country=["NL", "BE"], filter_harbor_use=["Commercial"])
            await client.vessels.positions(filter_ids=["9363728", "9321483"])
            assert _params(vessels).get_list("filter.flag") == ["GB", "NO"]
            assert _params(vessels).get_list("filter.vesselType") == ["Tug"]
            assert _params(ports).get_list("filter.country") == ["NL", "BE"]
            assert _params(ports).get_list("filter.harborUse") == ["Commercial"]
            assert _params(positions).get_list("filter.ids") == ["9363728", "9321483"]
            await client.aclose()

    @pytest.mark.asyncio
    async def test_async_iterators_forward_lists(self) -> None:
        from vessel_api_python import AsyncVesselClient

        with respx.mock() as mock:
            vessels = mock.get("https://api.vesselapi.com/v1/search/vessels").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            positions = mock.get("https://api.vesselapi.com/v1/vessels/positions").mock(
                return_value=httpx.Response(200, json={"vesselPositions": [], "nextToken": None})
            )
            client = AsyncVesselClient(api_key="key", max_retries=0)
            async for _ in client.search.all_vessels(filter_flag=["GB", "NO"]):
                pass
            async for _ in client.vessels.all_positions(filter_ids=["9363728", "9321483"]):
                pass
            assert _params(vessels).get_list("filter.flag") == ["GB", "NO"]
            assert _params(positions).get_list("filter.ids") == ["9363728", "9321483"]
            await client.aclose()


class TestRequiredParamsAreEnforced:
    """Params the spec marks required must be required in the signature too.

    They used to default to None, so the call typechecked, went out without the
    param and came back HTTP 400. Omitting one is now a TypeError at the call.
    """

    @pytest.mark.parametrize(
        ("service", "method", "kwargs", "missing"),
        [
            # location: bounding boxes need all four bounds, radius all three.
            ("location", "vessels_radius", {"latitude": 51.9}, "longitude"),
            ("location", "vessels_radius", {"latitude": 51.9, "longitude": 4.5}, "radius"),
            ("location", "ports_radius", {}, "latitude"),
            ("location", "dgps_radius", {}, "latitude"),
            ("location", "light_aids_radius", {}, "latitude"),
            ("location", "modus_radius", {}, "latitude"),
            ("location", "radio_beacons_radius", {}, "latitude"),
            ("location", "vessels_bounding_box", {"lat_min": 51.0, "lat_max": 52.0, "lon_min": 3.0}, "lon_max"),
            ("location", "ports_bounding_box", {}, "lat_min"),
            ("location", "dgps_bounding_box", {}, "lat_min"),
            ("location", "light_aids_bounding_box", {}, "lat_min"),
            ("location", "modus_bounding_box", {}, "lat_min"),
            ("location", "radio_beacons_bounding_box", {}, "lat_min"),
            # search: the four name-only endpoints reject a bare call.
            ("search", "dgps", {}, "filter_name"),
            ("search", "light_aids", {}, "filter_name"),
            ("search", "modus", {}, "filter_name"),
            ("search", "radio_beacons", {}, "filter_name"),
            # port events by name search.
            ("port_events", "by_ports", {"time_from": "2026-08-01T00:00:00Z"}, "filter_port_name"),
            ("port_events", "by_vessels", {"time_from": "2026-08-01T00:00:00Z"}, "filter_vessel_name"),
            # vessels.positions is meaningless without ids.
            ("vessels", "positions", {"filter_id_type": "mmsi"}, "filter_ids"),
            # The iterators enforce the same set.
            ("location", "all_vessels_radius", {"latitude": 51.9, "longitude": 4.5}, "radius"),
            ("location", "all_ports_bounding_box", {}, "lat_min"),
            ("search", "all_dgps", {}, "filter_name"),
            ("port_events", "all_by_ports", {}, "filter_port_name"),
            ("port_events", "all_by_vessels", {}, "filter_vessel_name"),
            ("vessels", "all_positions", {}, "filter_ids"),
        ],
    )
    def test_omitting_a_required_param_raises_type_error(
        self, service: str, method: str, kwargs: dict[str, object], missing: str
    ) -> None:
        client = VesselClient(api_key="key", max_retries=0)
        fn = getattr(getattr(client, service), method)
        with pytest.raises(TypeError, match=missing):
            fn(**kwargs)
        client.close()

    @pytest.mark.asyncio
    async def test_async_omitting_a_required_param_raises_type_error(self) -> None:
        """Binding happens at the call, so this raises without ever being awaited."""
        from vessel_api_python import AsyncVesselClient

        client = AsyncVesselClient(api_key="key", max_retries=0)
        with pytest.raises(TypeError, match="radius"):
            client.location.vessels_radius(latitude=51.9, longitude=4.5)  # type: ignore[call-arg]
        with pytest.raises(TypeError, match="filter_name"):
            client.search.dgps()  # type: ignore[call-arg]
        with pytest.raises(TypeError, match="filter_ids"):
            client.vessels.all_positions()  # type: ignore[call-arg]
        await client.aclose()

    def test_supplying_them_still_reaches_the_wire(self) -> None:
        """The required form must send exactly what it always sent."""
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/location/vessels/radius").mock(
                return_value=httpx.Response(200, json={"vessels": [], "nextToken": None})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.location.vessels_radius(latitude=51.9225, longitude=4.47917, radius=10000)
            params = _params(route)
            assert params.get("filter.latitude") == "51.9225"
            assert params.get("filter.longitude") == "4.47917"
            assert params.get("filter.radius") == "10000"
            client.close()

    def test_filter_id_type_stays_defaulted(self) -> None:
        """The spec requires it, but the SDK always sends it, so a default is safe."""
        with respx.mock() as mock:
            route = mock.get("https://api.vesselapi.com/v1/vessel/9363728").mock(
                return_value=httpx.Response(200, json={"vessel": {"imo": 9363728}})
            )
            client = VesselClient(api_key="key", max_retries=0)
            client.vessels.get("9363728")
            assert _params(route).get("filter.idType") == "imo"
            client.close()


class TestRequiredFlagsMatchTheSpec:
    """Read the spec and the source: no required param may carry a default.

    Reads the committed spec, so a spec change that marks a param required fails
    here rather than shipping a signature that 400s at runtime.
    """

    #: Required by the spec, but the SDK supplies it on every call, so a default
    #: can never produce a request that omits it.
    ALWAYS_SENT = {"filter.idType"}

    @staticmethod
    def _bindings() -> list[tuple[str, str, str, str, bool]]:
        """(class, method, wire param, python param, has_default) for required params."""
        import ast
        import json
        import pathlib
        import re

        root = pathlib.Path(__file__).resolve().parent.parent
        spec = json.loads((root / "openapi" / "swagger.json").read_text())
        tree = ast.parse((root / "src" / "vessel_api_python" / "_services.py").read_text())

        required_by_path = {
            re.sub(r"\{[^}]+\}", "{X}", path): {
                p["name"]
                for p in ops.get("get", {}).get("parameters", [])
                if p.get("in") == "query" and p.get("required")
            }
            for path, ops in spec["paths"].items()
        }

        func_types = (ast.FunctionDef, ast.AsyncFunctionDef)
        out = []
        for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
            for fn in [n for n in cls.body if isinstance(n, func_types)]:
                for node in ast.walk(fn):
                    is_client_get = (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "get"
                        and isinstance(node.func.value, ast.Attribute)
                        and node.func.value.attr == "_client"
                    )
                    if not is_client_get:
                        continue
                    path = re.sub(r"\{[^}]+\}", "{X}", ast.unparse(node.args[0]).lstrip("f").strip("\"'"))
                    wire_to_py = {}
                    for kw in node.keywords:
                        if kw.arg != "params":
                            continue
                        d = kw.value.args[0] if isinstance(kw.value, ast.Call) else kw.value
                        assert isinstance(d, ast.Dict)
                        for k, v in zip(d.keys, d.values):
                            assert isinstance(k, ast.Constant)
                            wire_to_py[k.value] = ast.unparse(v)
                    defaults = dict(zip([a.arg for a in fn.args.kwonlyargs], fn.args.kw_defaults))
                    for wire in sorted(required_by_path[path]):
                        py = wire_to_py[wire]
                        out.append((cls.name, fn.name, wire, py, defaults[py] is not None))
                    break
        return out

    def test_no_required_param_carries_a_default(self) -> None:
        offenders = [
            f"{cls}.{meth}({py}=) for {wire}"
            for cls, meth, wire, py, has_default in self._bindings()
            if has_default and wire not in self.ALWAYS_SENT
        ]
        assert offenders == []

    def test_every_required_param_is_keyword_only(self) -> None:
        """Positional would let a caller pass them in the wrong order silently."""
        import inspect

        from vessel_api_python import _services

        offenders = []
        for cls_name, meth, _wire, py, _d in self._bindings():
            fn = getattr(getattr(_services, cls_name), meth)
            param = inspect.signature(fn).parameters[py]
            if param.kind is not inspect.Parameter.KEYWORD_ONLY:
                offenders.append(f"{cls_name}.{meth}.{py} is {param.kind}")
        assert offenders == []

    def test_required_binding_count(self) -> None:
        """Guards the total so a new endpoint cannot quietly reintroduce a default."""
        bindings = self._bindings()
        enforced = [b for b in bindings if not b[4]]
        assert len(bindings) == 114
        assert len(enforced) == 98


class TestSpecQueryParamCoverage:
    """Every query param the spec declares must be reachable from the SDK.

    Reads the committed spec and the client source, so a spec update that adds a
    param fails here rather than silently going unreachable.
    """

    @staticmethod
    def _spec_vs_client() -> dict[str, set[str]]:
        # Parsed with ast rather than by regex over the source text. An earlier
        # version read only as far as the newline after the request call, so it
        # saw every parameter of a single-line call and none of a wrapped one.
        # Running the project's own `make fmt` wrapped those calls and turned
        # this check into a false alarm on all 29 endpoints.
        import ast
        import json
        import pathlib
        import re

        root = pathlib.Path(__file__).resolve().parent.parent
        spec = json.loads((root / "openapi" / "swagger.json").read_text())
        src = (root / "src" / "vessel_api_python" / "_services.py").read_text()

        def literal_path(node: ast.expr) -> str | None:
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            if isinstance(node, ast.JoinedStr):
                out = ""
                for part in node.values:
                    if isinstance(part, ast.Constant) and isinstance(part.value, str):
                        out += part.value
                    else:
                        out += "{X}"  # an interpolated path segment
                return out
            return None

        sent: dict[str, set[str]] = {}
        for node in ast.walk(ast.parse(src)):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "get"):
                continue
            if not node.args:
                continue
            raw = literal_path(node.args[0])
            if raw is None:
                continue
            path = re.sub(r"\{[^}]+\}", "{X}", raw)
            keys = {
                key.value
                for sub in ast.walk(node)
                if isinstance(sub, ast.Dict)
                for key in sub.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            }
            sent.setdefault(path, set()).update(keys)

        missing: dict[str, set[str]] = {}
        for path, ops in spec["paths"].items():
            declared = {p["name"] for p in ops.get("get", {}).get("parameters", []) if p.get("in") == "query"}
            gap = declared - sent.get(re.sub(r"\{[^}]+\}", "{X}", path), set())
            if gap:
                missing[path] = gap
        return missing

    def test_no_declared_query_param_is_unreachable(self) -> None:
        assert self._spec_vs_client() == {}
