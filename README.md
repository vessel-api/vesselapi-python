# vesselapi-python

[![CI](https://github.com/vessel-api/vesselapi-python/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/vessel-api/vesselapi-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/vessel-api-python.svg)](https://pypi.org/project/vessel-api-python/)
[![Python](https://img.shields.io/pypi/pyversions/vessel-api-python.svg)](https://pypi.org/project/vessel-api-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Python client for the [Vessel Tracking API](https://vesselapi.com) — maritime vessel tracking, port events, emissions, and navigation data.

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
| `vessels` | `get`, `position`, `casualties`, `classification`, `emissions`, `eta`, `inspections`, `inspection_detail`, `ownership`, `positions` | Vessel details, positions, and records |
| `ports` | `get` | Port lookup by UN/LOCODE |
| `port_events` | `list`, `by_port`, `by_ports`, `by_vessel`, `last_by_vessel`, `by_vessels` | Vessel arrival/departure events |
| `emissions` | `list` | EU MRV emissions data |
| `search` | `vessels`, `ports`, `dgps`, `light_aids`, `modus`, `radio_beacons` | Full-text search across entity types |
| `location` | `vessels_bounding_box`, `vessels_radius`, `ports_bounding_box`, `ports_radius`, `dgps_bounding_box`, `dgps_radius`, `light_aids_bounding_box`, `light_aids_radius`, `modus_bounding_box`, `modus_radius`, `radio_beacons_bounding_box`, `radio_beacons_radius` | Geo queries by bounding box or radius |
| `navtex` | `list` | NAVTEX maritime safety messages |

**37 methods total.**

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
        print("Rate limited — back off")
    elif err.is_auth_error:
        print("Check API key")
    print(err.status_code, err.message)
```

## Auto-Pagination

Every list endpoint has an `all_*` / `list_all` variant returning an iterator:

```python
# Sync
for vessel in client.search.all_vessels(filter_name="tanker"):
    print(vessel.name)

# Async
async for vessel in client.search.all_vessels(filter_name="tanker"):
    print(vessel.name)

# Collect all at once
vessels = client.search.all_vessels(filter_name="tanker").collect()
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

- [API Documentation](https://vesselapi.com/docs) — endpoint guides, request/response schemas, and usage examples
- [API Explorer](https://vesselapi.com/api-reference) — interactive API reference
- [Dashboard](https://dashboard.vesselapi.com) — manage API keys and monitor usage

## Contributing & Support

Found a bug, have a feature request, or need help? You're welcome to [open an issue](https://github.com/vessel-api/vesselapi-python/issues). For API-level bugs and feature requests, please use the [main VesselAPI repository](https://github.com/vessel-api/VesselApi/issues).

For security vulnerabilities, **do not** open a public issue — email security@vesselapi.com instead. See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
