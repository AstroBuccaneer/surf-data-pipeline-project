import json
import pandas as pd
import os
from datetime import datetime

# Paths
RAW_PATH = "data/raw/"
PROCESSED_PATH = "data/processed/"

# Create processed folder if it doesn't exist
os.makedirs(PROCESSED_PATH, exist_ok=True)

def clean_buoy_data():
    """Clean and normalize raw NOAA buoy data."""

    print("Cleaning buoy data...")

    with open(f"{RAW_PATH}noaa_wave_data.json", "r") as f:
        raw_data = json.load(f)

    all_records = []

    for location_key, raw_text in raw_data.items():
        lines = raw_text.strip().split("\n")
        
        # First two lines are headers
        headers = lines[0].split()
        
        for line in lines[2:]:  # Skip header rows
            values = line.split()
            if len(values) >= 9:
                try:
                    record = {
                        "location": location_key,
                        "year": int(values[0]),
                        "month": int(values[1]),
                        "day": int(values[2]),
                        "hour": int(values[3]),
                        "minute": int(values[4]),
                        "wave_height_m": float(values[8]) if values[8] != "MM" else None,
                        "dominant_period_sec": float(values[9]) if len(values) > 9 and values[9] != "MM" else None,
                        "wind_speed_ms": float(values[6]) if values[6] != "MM" else None,
                        "source": "NOAA_NDBC"
                    }
                    all_records.append(record)
                except (ValueError, IndexError):
                    continue

    df = pd.DataFrame(all_records)
    output_path = f"{PROCESSED_PATH}buoy_data_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Buoy data cleaned — {len(df)} records saved to {output_path}")
    return df

def clean_storm_data():
    """Clean and normalize raw NOAA storm data."""

    print("Cleaning storm data...")

    with open(f"{RAW_PATH}noaa_storm_data.json", "r") as f:
        raw_data = json.load(f)

    all_records = []

    for location_key, lines in raw_data.items():
        for line in lines:
            values = line.split(",")
            if len(values) >= 10:
                try:
                    record = {
                        "location": location_key,
                        "year": values[0].strip().replace('"', ''),
                        "month": values[1].strip().replace('"', ''),
                        "event_type": values[12].strip().replace('"', ''),
                        "state": values[4].strip().replace('"', ''),
                        "magnitude": values[22].strip().replace('"', '') if len(values) > 22 else None,
                        "deaths_direct": values[17].strip().replace('"', '') if len(values) > 17 else None,
                        "source": "NOAA_STORM_EVENTS"
                    }
                    all_records.append(record)
                except (ValueError, IndexError):
                    continue

    df = pd.DataFrame(all_records)
    output_path = f"{PROCESSED_PATH}storm_data_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Storm data cleaned — {len(df)} records saved to {output_path}")
    return df

def clean_seismic_data():
    """Clean and normalize raw USGS seismic data."""

    print("Cleaning seismic data...")

    with open(f"{RAW_PATH}usgs_seismic_data.json", "r") as f:
        raw_data = json.load(f)

    all_records = []

    for location_key, geojson in raw_data.items():
        features = geojson.get("features", [])
        
        for feature in features:
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            coords = geometry.get("coordinates", [None, None, None])

            try:
                record = {
                    "location": location_key,
                    "magnitude": props.get("mag"),
                    "place": props.get("place"),
                    "time": datetime.utcfromtimestamp(
                        props.get("time") / 1000
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "depth_km": coords[2],
                    "longitude": coords[0],
                    "latitude": coords[1],
                    "event_type": props.get("type"),
                    "source": "USGS"
                }
                all_records.append(record)
            except (ValueError, TypeError):
                continue

    df = pd.DataFrame(all_records)
    output_path = f"{PROCESSED_PATH}seismic_data_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Seismic data cleaned — {len(df)} records saved to {output_path}")
    return df

def clean_benchmarks():
    """Clean and normalize benchmark reference data."""

    print("Cleaning benchmark data...")

    with open(f"{RAW_PATH}benchmarks.json", "r") as f:
        raw_data = json.load(f)

    all_records = []

    for key, benchmark in raw_data.items():
        record = {
            "benchmark_key": key,
            "name": benchmark.get("name"),
            "location": benchmark.get("location"),
            "year": benchmark.get("year"),
            "wave_height_ft": benchmark.get("wave_height_ft"),
            "wave_height_m": benchmark.get("wave_height_m"),
            "cause": benchmark.get("cause"),
            "cause_type": benchmark.get("cause_type"),
            "surfable": benchmark.get("surfable"),
            "surfer": benchmark.get("surfer", "N/A"),
            "notes": benchmark.get("notes"),
            "source": "HARDCODED_RESEARCH"
        }
        all_records.append(record)

    df = pd.DataFrame(all_records)
    output_path = f"{PROCESSED_PATH}benchmarks_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Benchmark data cleaned — {len(df)} records saved to {output_path}")
    return df


if __name__ == "__main__":
    print("Starting data cleaning pipeline...\n")

    buoy_df = clean_buoy_data()
    storm_df = clean_storm_data()
    seismic_df = clean_seismic_data()
    benchmark_df = clean_benchmarks()

    print("\n--- Cleaning Summary ---")
    print(f"Buoy records    : {len(buoy_df)}")
    print(f"Storm records   : {len(storm_df)}")
    print(f"Seismic records : {len(seismic_df)}")
    print(f"Benchmarks      : {len(benchmark_df)}")
    print("\n✓ All data cleaned and saved to data/processed/")