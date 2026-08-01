import requests
import json
import time
import yaml
import os
from datetime import datetime

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# NOAA NDBC base URL
BASE_URL = "https://www.ndbc.noaa.gov/data/realtime2"

# Output path
RAW_PATH = "data/raw/"

print("✓ Live buoy stream initialized")


def fetch_live_reading(buoy_id):
    """Fetch the latest reading from a NOAA buoy."""

    url = f"{BASE_URL}/{buoy_id}.txt"
    response = requests.get(url)

    if response.status_code == 200:
        lines = response.text.strip().split("\n")
        if len(lines) >= 3:
            latest = lines[2].split()
            if len(latest) >= 9:
                try:
                    return {
                        "timestamp": datetime.utcnow().isoformat(),
                        "year": int(latest[0]),
                        "month": int(latest[1]),
                        "day": int(latest[2]),
                        "hour": int(latest[3]),
                        "minute": int(latest[4]),
                        "wave_height_m": float(latest[8]) if latest[8] != "MM" else None,
                        "wind_speed_ms": float(latest[6]) if latest[6] != "MM" else None,
                        "dominant_period_sec": float(latest[9]) if len(latest) > 9 and latest[9] != "MM" else None
                    }
                except (ValueError, IndexError):
                    return None
    return None


def stream_live_data(interval_seconds=3600, max_runs=None):
    """Stream live buoy data on a schedule."""

    print(f"Starting live buoy stream — polling every {interval_seconds} seconds...")
    print("Press Ctrl+C to stop\n")

    run_count = 0

    while True:
        run_count += 1
        print(f"\n--- Poll #{run_count} at {datetime.utcnow().isoformat()} ---")

        live_readings = {}

        for location_key, location_data in config["locations"].items():
            buoy_id = location_data["noaa_buoy_id"]
            print(f"Fetching live reading for {location_data['name']}...")

            reading = fetch_live_reading(buoy_id)

            if reading:
                live_readings[location_key] = reading
                wave = reading.get("wave_height_m")
                print(f"✓ {location_data['name']} — wave height: {wave}m")
            else:
                print(f"✗ No reading for {location_data['name']}")

        # Save live readings
        output_path = f"{RAW_PATH}live_buoy_readings.json"
        with open(output_path, "w") as f:
            json.dump({
                "poll_timestamp": datetime.utcnow().isoformat(),
                "poll_number": run_count,
                "readings": live_readings
            }, f, indent=4)

        print(f"\n✓ Live readings saved to {output_path}")

        # Check if max runs reached
        if max_runs and run_count >= max_runs:
            print(f"\n✓ Completed {max_runs} polling runs")
            break

        print(f"Waiting {interval_seconds} seconds until next poll...")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    # Run once for testing — remove max_runs for continuous streaming
    stream_live_data(interval_seconds=3600, max_runs=1)