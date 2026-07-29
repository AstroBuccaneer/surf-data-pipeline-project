import boto3
import json
import yaml
import sqlite3
from datetime import datetime

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Kinesis client
kinesis = boto3.client("kinesis", region_name=config["aws"]["region"])

# Stream name
STREAM_NAME = "surf-pipeline-live-buoy-stream"

# Database path
DB_PATH = "data/final/surf_pipeline.db"

print("✓ Kinesis consumer initialized")


def get_shard_iterator(shard_id):
    """Get shard iterator to start reading from stream."""

    response = kinesis.get_shard_iterator(
        StreamName=STREAM_NAME,
        ShardId=shard_id,
        ShardIteratorType="LATEST"
    )

    return response["ShardIterator"]


def process_record(record):
    """Process a single Kinesis record and save to database."""

    data = json.loads(record["Data"])
    reading = data.get("reading", {})

    if not reading or not reading.get("wave_height_m"):
        return None

    # Calculate benchmark percentages
    wave_height_m = reading["wave_height_m"]
    pct_of_nazare = round(wave_height_m / 26.2 * 100, 2)
    pct_of_lituya = round(wave_height_m / 524 * 100, 2)

    processed = {
        "location": data["location"],
        "buoy_id": data["buoy_id"],
        "timestamp": data["timestamp"],
        "wave_height_m": wave_height_m,
        "wind_speed_ms": reading.get("wind_speed_ms"),
        "dominant_period_sec": reading.get("dominant_period_sec"),
        "pct_of_nazare": pct_of_nazare,
        "pct_of_lituya": pct_of_lituya,
        "is_surfable": "Yes" if wave_height_m >= 1.5 else "No"
    }

    return processed


def save_to_database(processed_record):
    """Save processed record to SQLite database."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO wave_events (
            location_id, date_id, year, month,
            wave_height_m, dominant_period_sec,
            wind_speed_ms, benchmark_pct_nazare,
            benchmark_pct_lituya, source
        )
        SELECT
            l.location_id,
            CAST(strftime('%Y%m%d', ?) AS INTEGER),
            CAST(strftime('%Y', ?) AS INTEGER),
            CAST(strftime('%m', ?) AS INTEGER),
            ?, ?, ?, ?, ?, 'KINESIS_LIVE'
        FROM dim_location l
        WHERE l.location_key = ?
    """, (
        processed_record["timestamp"],
        processed_record["timestamp"],
        processed_record["timestamp"],
        processed_record["wave_height_m"],
        processed_record["dominant_period_sec"],
        processed_record["wind_speed_ms"],
        processed_record["pct_of_nazare"],
        processed_record["pct_of_lituya"],
        processed_record["location"]
    ))

    conn.commit()
    conn.close()
    print(f"✓ Saved live reading for {processed_record['location']} — {processed_record['wave_height_m']}m")


def run_consumer():
    """Run consumer continuously reading from Kinesis stream."""

    print("Starting Kinesis consumer...\n")

    # Get stream description to find shards
    response = kinesis.describe_stream(StreamName=STREAM_NAME)
    shards = response["StreamDescription"]["Shards"]

    print(f"✓ Found {len(shards)} shards in stream")

    # Get iterator for each shard
    iterators = []
    for shard in shards:
        iterator = get_shard_iterator(shard["ShardId"])
        iterators.append(iterator)

    # Continuously poll shards
    while True:
        new_iterators = []
        for iterator in iterators:
            response = kinesis.get_records(
                ShardIterator=iterator,
                Limit=100
            )

            records = response["Records"]
            if records:
                print(f"✓ Received {len(records)} records from Kinesis")
                for record in records:
                    processed = process_record(record)
                    if processed:
                        save_to_database(processed)

            new_iterators.append(response["NextShardIterator"])

        iterators = new_iterators


if __name__ == "__main__":
    run_consumer()