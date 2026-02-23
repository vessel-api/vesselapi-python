"""Basic asynchronous usage of the Vessel API Python SDK."""

import asyncio
import os
import sys

from vessel_api_python import AsyncVesselClient, VesselAPIError


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

        # Get vessel details by IMO number (defaults to IMO; pass filter_id_type="mmsi" for MMSI).
        print("\n--- Vessel by IMO ---")
        vessel = await client.vessels.get("9811000")
        if vessel.vessel:
            print(f"Vessel: {vessel.vessel.name} (Type: {vessel.vessel.vessel_type})")

        # Get the vessel's latest AIS position.
        print("\n--- Vessel Position ---")
        pos = await client.vessels.position("9811000")
        if pos.vessel_position:
            print(f"Position: {pos.vessel_position.latitude}, {pos.vessel_position.longitude}")

        # Find vessels within 10 km of Rotterdam.
        print("\n--- Vessels Near Rotterdam ---")
        nearby = await client.location.vessels_radius(latitude=51.9225, longitude=4.47917, radius=10000)
        for v in nearby.vessels or []:
            print(f"{v.vessel_name} (IMO: {v.imo}) at {v.latitude}, {v.longitude}")

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
