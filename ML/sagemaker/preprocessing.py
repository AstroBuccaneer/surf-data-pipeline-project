import pandas as pd
import numpy as np
import os
import json
import boto3
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Paths
PROCESSED_PATH = "data/processed/"
FINAL_PATH = "data/final/"

# S3 config
S3_BUCKET = "surf-pipeline-processed-agl"

print("✓ Preprocessing initialized")


def load_and_prepare_data():
    """Load cleaned data and prepare for ML feature engineering."""

    print("Loading data for ML preprocessing...")

    # Load buoy data
    buoy_df = pd.read_csv(f"{PROCESSED_PATH}buoy_data_clean.csv")

    # Load surf scores
    scores_df = pd.read_csv(f"{PROCESSED_PATH}surf_scores.csv")

    # Filter out null wave heights
    buoy_df = buoy_df.dropna(subset=["wave_height_m"])


    # Add wave height in feet
    buoy_df["wave_height_ft"] = (buoy_df["wave_height_m"] * 3.28084).round(2)

    # Add benchmark percentages
    buoy_df["pct_of_nazare"] = (buoy_df["wave_height_m"] / 26.2 * 100).round(2)
    buoy_df["pct_of_lituya"] = (buoy_df["wave_height_m"] / 524 * 100).round(2)

    # Add surfable flag
    buoy_df["is_surfable"] = (buoy_df["wave_height_m"] >= 1.5).astype(int)

    # Add season
    buoy_df["season"] = buoy_df["month"].apply(
        lambda m: "Winter" if m in [12, 1, 2] else
                  "Spring" if m in [3, 4, 5] else
                  "Summer" if m in [6, 7, 8] else "Fall"
    )

    # Add hurricane season flag
    buoy_df["is_hurricane_season"] = buoy_df["month"].apply(
        lambda m: 1 if m in [6, 7, 8, 9, 10, 11] else 0
    )

    print(f"✓ Loaded {len(buoy_df)} buoy records")
    print(f"✓ Loaded {len(scores_df)} location scores")

    return buoy_df, scores_df

def engineer_features(buoy_df):
    """Engineer features for surf score prediction model."""

    print("\nEngineering features...")

    # Aggregate by location and month for monthly features
    monthly_features = buoy_df.groupby(
        ["location", "year", "month"]
    ).agg(
        avg_wave_height_m=("wave_height_m", "mean"),
        max_wave_height_m=("wave_height_m", "max"),
        min_wave_height_m=("wave_height_m", "min"),
        std_wave_height_m=("wave_height_m", "std"),
        avg_wind_speed=("wind_speed_ms", "mean"),
        avg_period=("dominant_period_sec", "mean"),
        surfable_count=("is_surfable", "sum"),
        total_readings=("is_surfable", "count"),
        is_hurricane_season=("is_hurricane_season", "max")
    ).reset_index()

    # Add surfable percentage
    monthly_features["surfable_pct"] = (
        monthly_features["surfable_count"] /
        monthly_features["total_readings"] * 100
    ).round(2)

    # Add benchmark percentages
    monthly_features["pct_of_nazare"] = (
        monthly_features["avg_wave_height_m"] / 26.2 * 100
    ).round(2)

    # Add rolling 3 month average per location
    monthly_features = monthly_features.sort_values(["location", "year", "month"])
    monthly_features["rolling_3m_avg"] = monthly_features.groupby(
        "location"
    )["avg_wave_height_m"].transform(
        lambda x: x.rolling(3, min_periods=1).mean()
    ).round(2)

    # One hot encode location
    monthly_features = pd.get_dummies(
        monthly_features,
        columns=["location"],
        prefix="loc"
    )

    print(f"✓ Engineered {len(monthly_features)} monthly feature records")
    print(f"✓ Feature columns: {list(monthly_features.columns)}")

    return monthly_features


def split_and_scale(features_df):
    """Split data into train/test sets and scale features."""

    print("\nSplitting and scaling data...")

    # Define feature columns
    feature_cols = [
        "month",
        "avg_wave_height_m",
        "max_wave_height_m",
        "min_wave_height_m",
        "std_wave_height_m",
        "avg_wind_speed",
        "avg_period",
        "surfable_pct",
        "pct_of_nazare",
        "rolling_3m_avg",
        "is_hurricane_season"
    ] + [col for col in features_df.columns if col.startswith("loc_")]

   # Create location identifier before one hot encoding collapsed it
    loc_cols = [col for col in features_df.columns if col.startswith("loc_")]
    features_df["location_id"] = features_df[loc_cols].idxmax(axis=1)
    
    features_df["target"] = features_df.groupby(
        "location_id"
    )["avg_wave_height_m"].shift(-1)

    # Drop nulls from target
    features_df = features_df.dropna(subset=["target"])

    # Split features and target
    X = features_df[feature_cols]
    y = features_df["target"]

    # Train test split — 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"✓ Training set   : {X_train_scaled.shape[0]} records")
    print(f"✓ Test set       : {X_test_scaled.shape[0]} records")
    print(f"✓ Feature count  : {X_train_scaled.shape[1]} features")

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_cols


def save_preprocessed_data(X_train, X_test, y_train, y_test, scaler, feature_cols):
    """Save preprocessed data to final folder."""

    print("\nSaving preprocessed data...")

    os.makedirs(FINAL_PATH, exist_ok=True)

    # Save train and test sets
    pd.DataFrame(X_train).to_csv(
        f"{FINAL_PATH}X_train.csv", index=False
    )
    pd.DataFrame(X_test).to_csv(
        f"{FINAL_PATH}X_test.csv", index=False
    )
    pd.DataFrame(y_train).to_csv(
        f"{FINAL_PATH}y_train.csv", index=False
    )
    pd.DataFrame(y_test).to_csv(
        f"{FINAL_PATH}y_test.csv", index=False
    )

    # Save feature columns list
    with open(f"{FINAL_PATH}feature_cols.json", "w") as f:
        json.dump(feature_cols, f)

    print(f"✓ X_train saved  : {FINAL_PATH}X_train.csv")
    print(f"✓ X_test saved   : {FINAL_PATH}X_test.csv")
    print(f"✓ y_train saved  : {FINAL_PATH}y_train.csv")
    print(f"✓ y_test saved   : {FINAL_PATH}y_test.csv")
    print(f"✓ Feature cols saved : {FINAL_PATH}feature_cols.json")


if __name__ == "__main__":
    print("Starting SageMaker preprocessing...\n")

    # Load and prepare data
    buoy_df, scores_df = load_and_prepare_data()

    # Engineer features
    features_df = engineer_features(buoy_df)

    # Split and scale
    X_train, X_test, y_train, y_test, scaler, feature_cols = split_and_scale(
        features_df
    )

    # Save preprocessed data
    save_preprocessed_data(
        X_train, X_test, y_train, y_test, scaler, feature_cols
    )

    print("\n✓ SageMaker preprocessing complete!")


