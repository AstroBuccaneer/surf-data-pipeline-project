import boto3
import json
import time
import requests
import yaml
from datetime import datetime

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Kinesis client
kinesis = boto3.client("kinesis", region_name=config["aws"]["region"])

# Stream name
STREAM_NAME = "surf-pipeline-live-buoy-stream"

# NOAA NDBC base URL
BASE_URL = "https://www.ndbc.noaa.gov/data/realtime2"

print("✓ Kinesis producer initialized")


def fetch_live_buoy_reading(buoy_id):
    """Fetch latest buoy reading from NOAA NDBC."""

    url = f"{BASE_URL}/{buoy_id}.txt"
    response = requests.get(url)

    if response.status_code == 200:
        lines = response.text.strip().split("\n")
        # Get most recent reading (line 2 is latest)
        if len(lines) >= 3:
            latest = lines[2].split()
            if len(latest) >= 9:
                try:
                    return {
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


def send_to_kinesis(location_key, buoy_id, reading):
    """Send buoy reading to Kinesis stream."""

    record = {
        "location": location_key,
        "buoy_id": buoy_id,
        "timestamp": datetime.utcnow().isoformat(),
        "reading": reading
    }

    response = kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(record),
        PartitionKey=location_key
    )

    return response["ShardId"]


def run_producer(interval_seconds=3600):
    """Run producer continuously fetching live buoy data."""

    print(f"Starting live buoy stream — polling every {interval_seconds} seconds...\n")

    while True:
        for location_key, location_data in config["locations"].items():
            buoy_id = location_data["noaa_buoy_id"]
            print(f"Fetching live reading for {location_data['name']}...")

            reading = fetch_live_buoy_reading(buoy_id)

            if reading:
                shard_id = send_to_kinesis(location_key, buoy_id, reading)
                print(f"✓ Sent to Kinesis shard {shard_id} — wave height: {reading['wave_height_m']}m")
            else:
                print(f"✗ No reading available for {location_data['name']}")

        print(f"\nWaiting {interval_seconds} seconds until next poll...\n")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_producer(interval_seconds=3600)