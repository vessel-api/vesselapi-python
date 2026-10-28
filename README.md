# vesselapi-python

[![CI](https://github.com/vessel-api/vesselapi-python/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/vessel-api/vesselapi-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/vessel-api-python.svg)](https://pypi.org/project/vessel-api-python/)
[![Python](https://img.shields.io/pypi/pyversions/vessel-api-python.svg)](https://pypi.org/project/vessel-api-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Python client for the [Vessel Tracking API](https://vesselapi.com): maritime vessel tracking, port events, emissions, and nautical infrastructure.

**Resources**: [Documentation](https://vesselapi.com/docs) | [API Explorer](https://vesselapi.com/api-reference) | [Dashboard](https://dashboard.vesselapi.com) | [Contact Support](mailto:support@vesselapi.com)

## Install

```bash
pip install vessel-api-python
```

Requires Python 3.9+.

## Quick Start

```python
from vessel_api_python import VesselClient

client = VesselClient(api_key="your-api-key")

# Search for a vessel by name.
result = client.search.vessels(filter_name="Ever Given")
for v in result.vessels or []:
    print(f"{v.name} (IMO {v.imo})")

# Get a port by UN/LOCODE.
port = client.ports.get("NLRTM")
print(port.port.name)

# Auto-paginate through port events.
for event in client.port_events.list_all(pagination_limit=10):
    print(f"{event.event} at {event.timestamp}")
```

### Async

```python
import asyncio
from vessel_api_python import AsyncVesselClient

async def main():
    async with AsyncVesselClient(api_key="your-api-key") as client:
        result = await client.search.vessels(filter_name="Ever Given")
        async for event in client.port_events.list_all(pagination_limit=10):
            print(f"{event.event} at {event.timestamp}")

asyncio.run(main())
```

## Available Services

| Service | Methods | Description |
|---------|---------|-------------|
| `vessels` | `get`, `position`, `casualties`, `emissions`, `eta`, `positions` | Vessel details, positions, and records |
| `ports` | `get`, `inbound`, `inbound_all` | Port lookup by UN/LOCODE and inbound vessels |
| `port_events` | `list`, `by_port`, `by_ports`, `by_vessel`, `last_by_vessel`, `by_vessels` | Vessel arrival/departure events |
| `emissions` | `list` | EU MRV emissions data |
| `search` | `vessels`, `ports`, `dgps`, `light_aids`, `modus`, `radio_beacons` | Full-text search across entity types |
| `location` | `vessels_bounding_box`, `vessels_radius`, `ports_bounding_box`, `ports_radius`, `dgps_bounding_box`, `dgps_radius`, `light_aids_bounding_box`, `light_aids_radius`, `modus_bounding_box`, `modus_radius`, `radio_beacons_bounding_box`, `radio_beacons_radius` | Geo queries by bounding box or radius |

**33 methods total**, one per API endpoint, plus 28 auto-pagination iterators.

## Required Parameters

Parameters the API requires are keyword-only with no default, so leaving one out
raises `TypeError` at the call instead of returning HTTP 400 from the server:

```python
client.location.vessels_radius(latitude=51.9225, longitude=4.47917, radius=10000)
client.location.vessels_radius(latitude=51.9225)  # TypeError: missing longitude, radius
```

This covers the geo bounds on every `location` method (`lat_min`, `lat_max`,
`lon_min`, `lon_max` for bounding boxes; `latitude`, `longitude`, `radius` for
radius queries), `filter_name` on `search.dgps`, `search.light_aids`,
`search.modus` and `search.radio_beacons`, `filter_port_name` on
`port_events.by_ports`, `filter_vessel_name` on `port_events.by_vessels`, and
`filter_ids` on `vessels.positions`, along with the matching `all_*` iterators.
`filter_id_type` is required by the API but keeps its `"imo"` default, since the
SDK always sends it.

## Vessel Lookup & Location

```python
# Get vessel details by IMO number (defaults to IMO; pass filter_id_type="mmsi" for MMSI).
vessel = client.vessels.get("9811000")
print(f"{vessel.vessel.name} ({vessel.vessel.vessel_type})")

# Get a vessel's latest stored AIS position. A vessel that exists may have no
# stored position, which raises VesselNotFoundError rather than returning empty.
pos = client.vessels.position("232003239", filter_id_type="mmsi")
print(f"Position: {pos.vessel_position.latitude}, {pos.vessel_position.longitude}")

# filter_sat=True falls back to satellite AIS when no recent terrestrial position is stored.
# ⚠️ Satellite lookups draw on a prepaid balance: a credit is charged when a satellite fix is returned.
# Omit it unless you need that fallback.

# Find vessels with an AIS position within 10 km of Rotterdam in the last 2 hours
# (the default time window, at most 4 hours).
nearby = client.location.vessels_radius(latitude=51.9225, longitude=4.47917, radius=10000)
for v in nearby.vessels or []:
    print(f"{v.vessel_name} at {v.latitude}, {v.longitude}")
```

## Search

`search.vessels` accepts `q`, a unified search across IMO, MMSI, ENI, callsign and
name. One value can return several vessels, and `_meta.matched_on` maps each result's
index to the fields it matched on.

```python
res = client.search.vessels(q="4606770")
print(res.meta.matched_on)  # {"0": ["eni"]}
```

Filters the API declares as repeatable take either one value or a list. A list is
sent as a repeated query parameter, so the values are OR-ed:

```python
# ?filter.flag=PA&filter.flag=LR&filter.vesselType=Container%20Ship
client.search.vessels(filter_flag=["PA", "LR"], filter_vessel_type="Container Ship")

client.search.ports(filter_country=["NL", "BE"], filter_size=["LARGE", "MEDIUM"])
```

These are `filter_flag` and `filter_vessel_type` on `search.vessels`;
`filter_country`, `filter_port_type`, `filter_size`, `filter_harbor_size` and
`filter_harbor_use` on `search.ports`; and `filter_ids` on `vessels.positions`,
which also accepts the comma-separated single-string form.

## Error Handling

All methods raise specific exception types on non-2xx responses:

```python
from vessel_api_python import VesselAPIError

try:
    client.ports.get("ZZZZZ")
except VesselAPIError as err:
    if err.is_not_found:
        print("Port not found")
    elif err.is_rate_limited:
        print("Rate limited, backing off")
    elif err.is_auth_error:
        print("Check API key")
    print(err.status_code, err.message)
```

## Auto-Pagination

Every list endpoint has an `all_*` / `list_all` variant returning an iterator:

```python
# Sync
for vessel in client.search.all_vessels(filter_vessel_type="Tanker"):
    print(vessel.name)

# Async
async for vessel in client.search.all_vessels(filter_vessel_type="Tanker"):
    print(vessel.name)

# Collect every match at once. pagination_limit is the page size, not a total:
# .collect() walks to the end, so this is one request per page until exhausted.
vessels = client.search.all_vessels(filter_vessel_type="Tanker", pagination_limit=50).collect()

# To take a fixed number, stop the iterator yourself.
from itertools import islice

first_50 = list(islice(client.search.all_vessels(filter_vessel_type="Tanker"), 50))
```

## Configuration

```python
client = VesselClient(
    api_key="your-api-key",
    base_url="https://custom-endpoint.example.com/v1",
    timeout=60.0,
    max_retries=5,  # default: 3
    user_agent="my-app/1.0",
)
```

Retries use exponential backoff with jitter on 429 and 5xx responses. The `Retry-After` header is respected.

## Documentation

- [API Documentation](https://vesselapi.com/docs): endpoint guides, request/response schemas, and usage examples
- [API Explorer](https://vesselapi.com/api-reference): interactive API reference
- [Dashboard](https://dashboard.vesselapi.com): manage API keys and monitor usage

## Contributing & Support

Found a bug, have a feature request, or need help? You're welcome to [open an issue](https://github.com/vessel-api/vesselapi-python/issues). For API-level bugs and feature requests, please use the [main VesselAPI repository](https://github.com/vessel-api/VesselApi/issues).

For security vulnerabilities, **do not** open a public issue. Email security@vesselapi.com instead. See [SECURITY.md](SECURITY.md).

## Data Sources & Attribution

Emissions and casualty data: © European Union. Source: European Maritime Safety Agency
(EMSA): THETIS-MRV (EU MRV, Regulation (EU) 2015/757) and the European Marine Casualty
Information Platform (EMCIP). Reused under the European Commission reuse notice
(Commission Decision 2011/833/EU), which authorises reuse for commercial and
non-commercial purposes with acknowledgement of the source. Data may be transformed and
combined; EMSA does not endorse this service.

## License

[MIT](LICENSE)
