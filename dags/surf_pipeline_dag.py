from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add project root to path so Airflow can find our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our pipeline functions
from extract.noaa_buoy import fetch_all_locations
from extract.noaa_storms import fetch_all_storm_data
from extract.usgs_seismic import fetch_all_seismic_data
from extract.benchmarks import get_benchmarks
from transform.clean import clean_buoy_data, clean_storm_data, clean_seismic_data, clean_benchmarks
from transform.schema import create_dim_location, create_dim_cause, create_dim_date, create_dim_benchmark, create_fact_wave_events
from transform.score import calculate_final_surf_score



# Default arguments for all tasks
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5)
}

# Define the DAG
dag = DAG(
    "surf_pipeline",
    default_args=default_args,
    description="End to end surf data pipeline — extract, transform, score",
    schedule_interval="0 6 * * 1",  # Every Monday at 6am
    catchup=False,
    tags=["surf", "data-engineering", "noaa", "usgs"]
)




# ── Extract Tasks ────────────────────────────────────────────────────────────
def extract_buoy_data():
    data = fetch_all_locations("2020-01-01", "2023-12-31")
    import json
    with open("data/raw/noaa_wave_data.json", "w") as f:
        json.dump(data, f, indent=4)
    print("✓ Buoy extraction complete")

def extract_storm_data():
    data = fetch_all_storm_data("2000", "2023")
    import json
    with open("data/raw/noaa_storm_data.json", "w") as f:
        json.dump(data, f, indent=4)
    print("✓ Storm extraction complete")

def extract_seismic_data():
    data = fetch_all_seismic_data("2000-01-01", "2023-12-31")
    import json
    with open("data/raw/usgs_seismic_data.json", "w") as f:
        json.dump(data, f, indent=4)
    print("✓ Seismic extraction complete")

def extract_benchmark_data():
    data = get_benchmarks()
    import json
    with open("data/raw/benchmarks.json", "w") as f:
        json.dump(data, f, indent=4)
    print("✓ Benchmark extraction complete")

# ── Transform Tasks ──────────────────────────────────────────────────────────
def transform_clean():
    clean_buoy_data()
    clean_storm_data()
    clean_seismic_data()
    clean_benchmarks()
    print("✓ Cleaning complete")

def transform_schema():
    create_dim_location()
    create_dim_cause()
    create_dim_date()
    create_dim_benchmark()
    create_fact_wave_events()
    print("✓ Schema complete")

def transform_score():
    calculate_final_surf_score()
    print("✓ Scoring complete")


    # ── Define Tasks ─────────────────────────────────────────────────────────────
with dag:
    t1_buoy = PythonOperator(
        task_id="extract_buoy_data",
        python_callable=extract_buoy_data
    )

    t2_storms = PythonOperator(
        task_id="extract_storm_data",
        python_callable=extract_storm_data
    )

    t3_seismic = PythonOperator(
        task_id="extract_seismic_data",
        python_callable=extract_seismic_data
    )

    t4_benchmarks = PythonOperator(
        task_id="extract_benchmark_data",
        python_callable=extract_benchmark_data
    )

    t5_clean = PythonOperator(
        task_id="transform_clean",
        python_callable=transform_clean
    )

    t6_schema = PythonOperator(
        task_id="transform_schema",
        python_callable=transform_schema
    )

    t7_score = PythonOperator(
        task_id="transform_score",
        python_callable=transform_score
    )

    # ── Set Dependencies ──────────────────────────────────────────────────────
    [t1_buoy, t2_storms, t3_seismic, t4_benchmarks] >> t5_clean >> t6_schema >> t7_score

    