import pandas as pd
import sqlite3
import json
import os

# Database path
DB_PATH = "data/final/surf_pipeline.db"
PROCESSED_PATH = "data/processed/"

# Connect to database
conn = sqlite3.connect(DB_PATH)

print("✓ Connected to surf pipeline database")

def calculate_peak_magnitude_score():
    """Score each location based on max wave height vs Nazare benchmark."""

    print("Calculating peak magnitude scores...")

    query = """
        SELECT 
            l.name as location_name,
            l.location_key,
            MAX(w.wave_height_m) as max_wave_height_m,
            ROUND(MAX(w.wave_height_m) * 3.28084, 2) as max_wave_height_ft,
            ROUND(MAX(w.benchmark_pct_nazare), 2) as pct_of_nazare,
            ROUND(MAX(w.benchmark_pct_lituya), 2) as pct_of_lituya
        FROM wave_events w
        JOIN dim_location l ON w.location_id = l.location_id
        WHERE w.wave_height_m IS NOT NULL
        GROUP BY l.name, l.location_key
        ORDER BY max_wave_height_m DESC
    """

    df = pd.read_sql(query, conn)
    print(df.to_string(index=False))
    return df

def calculate_surfable_frequency_score():
    """Score each location based on frequency of surfable wave conditions."""

    print("\nCalculating surfable frequency scores...")

    # A wave is considered surfable if it's at least 1.5m (about 5ft)
    query = """
        SELECT
            l.name as location_name,
            l.location_key,
            COUNT(*) as total_readings,
            SUM(CASE WHEN w.wave_height_m >= 1.5 THEN 1 ELSE 0 END) as surfable_readings,
            ROUND(
                SUM(CASE WHEN w.wave_height_m >= 1.5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
            ) as surfable_pct,
            ROUND(AVG(w.wave_height_m), 2) as avg_wave_height_m
        FROM wave_events w
        JOIN dim_location l ON w.location_id = l.location_id
        WHERE w.wave_height_m IS NOT NULL
        GROUP BY l.name, l.location_key
        ORDER BY surfable_pct DESC
    """

    df = pd.read_sql(query, conn)
    print(df.to_string(index=False))
    return df


def calculate_seismic_recurrence_score():
    """Score each location based on seismic event frequency."""

    print("\nCalculating seismic recurrence scores...")

    seismic_df = pd.read_csv(f"{PROCESSED_PATH}seismic_data_clean.csv")

    # Count events per location and get max magnitude
    summary = seismic_df.groupby("location").agg(
        total_seismic_events=("magnitude", "count"),
        max_magnitude=("magnitude", "max"),
        avg_magnitude=("magnitude", "mean")
    ).reset_index()

    # Normalize to a 0-100 score based on event count
    max_events = summary["total_seismic_events"].max()
    summary["seismic_score"] = (
        summary["total_seismic_events"] / max_events * 100
    ).round(2)

    print(summary.to_string(index=False))
    return summary


def calculate_final_surf_score():
    """Combine all scores into final surf potential index."""

    print("\nCalculating final surf potential scores...")

    # Get all three scores
    peak_df = calculate_peak_magnitude_score()
    freq_df = calculate_surfable_frequency_score()
    seismic_df = calculate_seismic_recurrence_score()

    # Load scoring weights from config
    import yaml
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    weights = config["scoring"]
    peak_weight = weights["peak_magnitude_weight"]
    freq_weight = weights["surfable_event_frequency_weight"]
    seismic_weight = weights["cause_recurrence_weight"]

    # Normalize peak score to 0-100
    max_nazare_pct = peak_df["pct_of_nazare"].max()
    peak_df["peak_score"] = (
        peak_df["pct_of_nazare"] / max_nazare_pct * 100
    ).round(2)

    # Merge all scores
    final_df = peak_df[["location_name", "location_key", 
                          "max_wave_height_ft", "pct_of_nazare", 
                          "peak_score"]].copy()

    final_df = final_df.merge(
        freq_df[["location_key", "surfable_pct"]],
        on="location_key",
        how="left"
    )

    final_df = final_df.merge(
        seismic_df[["location", "seismic_score"]],
        left_on="location_key",
        right_on="location",
        how="left"
    ).drop(columns=["location"])

    # Calculate weighted final score
    final_df["surf_potential_score"] = (
        (final_df["peak_score"] * peak_weight) +
        (final_df["surfable_pct"] * freq_weight) +
        (final_df["seismic_score"] * seismic_weight)
    ).round(2)

    # Rank locations
    final_df["rank"] = final_df["surf_potential_score"].rank(
        ascending=False
    ).astype(int)

    final_df = final_df.sort_values("surf_potential_score", ascending=False)

    # Save to processed folder
    output_path = f"{PROCESSED_PATH}surf_scores.csv"
    final_df.to_csv(output_path, index=False)

    print("\n--- Final Surf Potential Rankings ---")
    print(final_df[["rank", "location_name", "max_wave_height_ft",
                     "pct_of_nazare", "surfable_pct", 
                     "seismic_score", "surf_potential_score"]].to_string(index=False))
    print(f"\n✓ Surf scores saved to {output_path}")
    return final_df


if __name__ == "__main__":
    print("Starting surf score calculation...\n")
    final_df = calculate_final_surf_score()
    conn.close()
    print("\n✓ Scoring complete!")