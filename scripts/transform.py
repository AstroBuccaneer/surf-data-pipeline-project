import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transform.clean import clean_buoy_data, clean_storm_data, clean_seismic_data, clean_benchmarks
from transform.schema import create_dim_location, create_dim_cause, create_dim_date, create_dim_benchmark, create_fact_wave_events
from transform.score import calculate_final_surf_score
import sqlite3

def run_transform():
    """Run full transformation pipeline."""

    print("=" * 60)
    print("SURF PIPELINE — TRANSFORM PHASE")
    print("=" * 60)

    # Clean all data sources
    print("\n[1/3] Cleaning raw data...")
    clean_buoy_data()
    clean_storm_data()
    clean_seismic_data()
    clean_benchmarks()
    print("✓ All data cleaned")

    # Build star schema
    print("\n[2/3] Building star schema...")
    conn = sqlite3.connect("data/final/surf_pipeline.db")
    create_dim_location()
    create_dim_cause()
    create_dim_date()
    create_dim_benchmark()
    create_fact_wave_events()
    conn.close()
    print("✓ Star schema built")

    # Calculate surf scores
    print("\n[3/3] Calculating surf scores...")
    calculate_final_surf_score()
    print("✓ Surf scores calculated")

    print("\n" + "=" * 60)
    print("✓ TRANSFORM PHASE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_transform()