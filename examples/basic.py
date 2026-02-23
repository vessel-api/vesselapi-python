"""Basic synchronous usage of the Vessel API Python SDK."""

import os
import sys

from vessel_api_python import VesselClient, VesselAPIError


def main() -> None:
    api_key = os.environ.get("VESSELAPI_API_KEY", "")
    if not api_key:
        print("VESSELAPI_API_KEY environment variable is required")
        sys.exit(1)

    client = VesselClient(api_key=api_key)

    # Search for vessels by name.
    print("--- Search Vessels ---")
    result = client.search.vessels(filter_name="Ever Given")
    for v in result.vessels or []:
        print(f"Vessel: {v.name} (IMO: {v.imo})")

    # Search for vessels by flag.
    print("\n--- Search Vessels by Flag ---")
    flag_result = client.search.vessels(filter_flag="PA", filter_vessel_type="Container Ship", pagination_limit=5)
    for v in flag_result.vessels or []:
        print(f"Vessel: {v.name} (IMO: {v.imo}, Country: {v.country})")

    # Search for ports by country.
    print("\n--- Search Ports by Country ---")
    port_search = client.search.ports(filter_country="NL", pagination_limit=5)
    for p in port_search.ports or []:
        print(f"Port: {p.name} ({p.unlo_code})")

    # Get a port by UNLOCODE.
    print("\n--- Get Port ---")
    port = client.ports.get("NLRTM")
    if port.port:
        print(f"Port: {port.port.name} ({port.port.unlo_code})")

    # Get vessel details by IMO number (defaults to IMO; pass filter_id_type="mmsi" for MMSI).
    print("\n--- Vessel by IMO ---")
    vessel = client.vessels.get("9811000")
    if vessel.vessel:
        print(f"Vessel: {vessel.vessel.name} (Type: {vessel.vessel.vessel_type})")

    # Get the vessel's latest AIS position.
    print("\n--- Vessel Position ---")
    pos = client.vessels.position("9811000")
    if pos.vessel_position:
        print(f"Position: {pos.vessel_position.latitude}, {pos.vessel_position.longitude}")
        print(f"Speed: {pos.vessel_position.sog} knots, Heading: {pos.vessel_position.heading}")

    # Find vessels within 10 km of Rotterdam.
    print("\n--- Vessels Near Rotterdam ---")
    nearby = client.location.vessels_radius(latitude=51.9225, longitude=4.47917, radius=10000)
    for v in nearby.vessels or []:
        print(f"{v.vessel_name} (IMO: {v.imo}) at {v.latitude}, {v.longitude}")

    # Handle a not-found port gracefully.
    print("\n--- Not Found Handling ---")
    try:
        client.ports.get("ZZZZZ")
    except VesselAPIError as err:
        if err.is_not_found:
            print(f"Port ZZZZZ not found (status {err.status_code})")
        elif err.is_rate_limited:
            print("Rate limited — try again later")
        else:
            print(f"API error: {err.message} (status {err.status_code})")

    # Auto-paginate through port events.
    print("\n--- Port Events (paginated) ---")
    count = 0
    for event in client.port_events.list_all(pagination_limit=10):
        print(f"Event: {event.event} at {event.timestamp}")
        count += 1
        if count >= 25:
            break
    print(f"Total events shown: {count}")

    client.close()


if __name__ == "__main__":
    main()
