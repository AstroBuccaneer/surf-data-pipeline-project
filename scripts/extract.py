import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract.noaa_buoy import fetch_all_locations
from extract.noaa_storms import fetch_all_storm_data
from extract.usgs_seismic import fetch_all_seismic_data
from extract.benchmarks import get_benchmarks

def run_extract():
    """Run full extraction pipeline."""

    print("=" * 60)
    print("SURF PIPELINE — EXTRACT PHASE")
    print("=" * 60)

    # Extract buoy data
    print("\n[1/4] Extracting NOAA buoy data...")
    buoy_data = fetch_all_locations("2010-01-01", "2023-12-31")
    with open("data/raw/noaa_wave_data.json", "w") as f:
        json.dump(buoy_data, f, indent=4)
    print("✓ Buoy data extracted")

    # Extract storm data
    print("\n[2/4] Extracting NOAA storm data...")
    storm_data = fetch_all_storm_data("2000", "2023")
    with open("data/raw/noaa_storm_data.json", "w") as f:
        json.dump(storm_data, f, indent=4)
    print("✓ Storm data extracted")

    # Extract seismic data
    print("\n[3/4] Extracting USGS seismic data...")
    seismic_data = fetch_all_seismic_data("2000-01-01", "2023-12-31")
    with open("data/raw/usgs_seismic_data.json", "w") as f:
        json.dump(seismic_data, f, indent=4)
    print("✓ Seismic data extracted")

    # Extract benchmarks
    print("\n[4/4] Loading benchmark reference data...")
    benchmarks = get_benchmarks()
    with open("data/raw/benchmarks.json", "w") as f:
        json.dump(benchmarks, f, indent=4)
    print("✓ Benchmarks loaded")

    print("\n" + "=" * 60)
    print("✓ EXTRACT PHASE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_extract()