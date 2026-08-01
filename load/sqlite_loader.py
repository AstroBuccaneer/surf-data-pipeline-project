import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database path
DB_PATH = "data/final/surf_pipeline.db"
PROCESSED_PATH = "data/processed/"

print("✓ SQLite loader initialized")


def get_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    print(f"✓ Connected to {DB_PATH}")
    return conn


def load_table(df, table_name, conn, if_exists="replace"):
    """Load a dataframe into a SQLite table."""
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", conn)["count"][0]
    print(f"✓ Loaded {count} records into {table_name}")


def load_all_processed_data():
    """Load all processed CSV files into SQLite."""

    print("\nLoading processed data into SQLite...")

    conn = get_connection()

    # Load buoy data
    buoy_df = pd.read_csv(f"{PROCESSED_PATH}buoy_data_clean.csv")
    load_table(buoy_df, "buoy_data_clean", conn)

    # Load storm data
    storm_df = pd.read_csv(f"{PROCESSED_PATH}storm_data_clean.csv")
    load_table(storm_df, "storm_data_clean", conn)

    # Load seismic data
    seismic_df = pd.read_csv(f"{PROCESSED_PATH}seismic_data_clean.csv")
    load_table(seismic_df, "seismic_data_clean", conn)

    # Load benchmarks
    benchmark_df = pd.read_csv(f"{PROCESSED_PATH}benchmarks_clean.csv")
    load_table(benchmark_df, "benchmarks_clean", conn)

    # Load surf scores
    scores_df = pd.read_csv(f"{PROCESSED_PATH}surf_scores.csv")
    load_table(scores_df, "surf_scores", conn)

    conn.close()
    print("\n✓ All processed data loaded into SQLite")


def verify_tables():
    """Verify all tables exist and have data."""

    print("\nVerifying SQLite tables...")

    conn = get_connection()
    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    print("\n--- SQLite Table Summary ---")
    for table in tables:
        count = cursor.execute(
            f"SELECT COUNT(*) FROM {table[0]}"
        ).fetchone()[0]
        print(f"{table[0]:<25} : {count:,} records")

    conn.close()


if __name__ == "__main__":
    print("Starting SQLite loader...\n")

    load_all_processed_data()
    verify_tables()

    print("\n✓ SQLite loader complete!")