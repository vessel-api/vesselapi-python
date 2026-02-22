"""Basic asynchronous usage of the Vessel API Python SDK."""

import asyncio
import os
import sys

from vesselapi import AsyncVesselClient, VesselAPIError


async def main() -> None:
    api_key = os.environ.get("VESSELAPI_API_KEY", "")
    if not api_key:
        print("VESSELAPI_API_KEY environment variable is required")
        sys.exit(1)

    async with AsyncVesselClient(api_key=api_key) as client:
        # Search for vessels.
        print("--- Search Vessels ---")
        result = await client.search.vessels(filter_name="Ever Given")
        for v in result.vessels or []:
            print(f"Vessel: {v.name} (IMO: {v.imo})")

        # Get a port.
        print("\n--- Get Port ---")
        port = await client.ports.get("NLRTM")
        if port.port:
            print(f"Port: {port.port.name} ({port.port.unlo_code})")

        # Error handling.
        print("\n--- Error Handling ---")
        try:
            await client.ports.get("ZZZZZ")
        except VesselAPIError as err:
            if err.is_not_found:
                print(f"Port not found (status {err.status_code})")

        # Auto-paginate (async).
        print("\n--- Port Events (async paginated) ---")
        count = 0
        async for event in client.port_events.list_all(pagination_limit=10):
            print(f"Event: {event.event} at {event.timestamp}")
            count += 1
            if count >= 25:
                break
        print(f"Total events shown: {count}")


if __name__ == "__main__":
    asyncio.run(main())
