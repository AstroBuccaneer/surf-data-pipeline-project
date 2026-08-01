import boto3
import json
import pandas as pd
import os
from datetime import datetime

# Paths
FINAL_PATH = "data/final/"
PROCESSED_PATH = "data/processed/"

# AWS config
REGION = "us-east-1"

print("✓ Feature Store definitions initialized")


def define_feature_group():
    """Define SageMaker Feature Store feature group schema."""

    feature_group_name = "surf-pipeline-features"

    feature_definitions = [
        {"FeatureName": "location_key",         "FeatureType": "String"},
        {"FeatureName": "year",                  "FeatureType": "Integral"},
        {"FeatureName": "month",                 "FeatureType": "Integral"},
        {"FeatureName": "avg_wave_height_m",     "FeatureType": "Fractional"},
        {"FeatureName": "max_wave_height_m",     "FeatureType": "Fractional"},
        {"FeatureName": "min_wave_height_m",     "FeatureType": "Fractional"},
        {"FeatureName": "std_wave_height_m",     "FeatureType": "Fractional"},
        {"FeatureName": "avg_wind_speed",        "FeatureType": "Fractional"},
        {"FeatureName": "avg_period",            "FeatureType": "Fractional"},
        {"FeatureName": "surfable_count",        "FeatureType": "Integral"},
        {"FeatureName": "total_readings",        "FeatureType": "Integral"},
        {"FeatureName": "surfable_pct",          "FeatureType": "Fractional"},
        {"FeatureName": "pct_of_nazare",         "FeatureType": "Fractional"},
        {"FeatureName": "rolling_3m_avg",        "FeatureType": "Fractional"},
        {"FeatureName": "is_hurricane_season",   "FeatureType": "Integral"},
        {"FeatureName": "event_time",            "FeatureType": "String"},
        {"FeatureName": "record_id",             "FeatureType": "String"}
    ]

    schema = {
        "feature_group_name": feature_group_name,
        "record_identifier": "record_id",
        "event_time_feature": "event_time",
        "feature_definitions": feature_definitions,
        "online_store_enabled": True,
        "offline_store_s3_uri": "s3://surf-pipeline-final-agl/feature-store/"
    }

    print(f"✓ Feature group defined: {feature_group_name}")
    print(f"✓ Total features: {len(feature_definitions)}")

    return schema


def prepare_features_for_store():
    """Prepare monthly features for ingestion into Feature Store."""

    print("\nPreparing features for Feature Store...")

    # Load training data
    X_train = pd.read_csv(f"{FINAL_PATH}X_train.csv")
    feature_cols = json.load(open(f"{FINAL_PATH}feature_cols.json"))

    # Add required Feature Store columns
    X_train["event_time"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    X_train["record_id"] = [f"surf-{i:05d}" for i in range(len(X_train))]

    output_path = f"{FINAL_PATH}feature_store_ready.csv"
    X_train.to_csv(output_path, index=False)

    print(f"✓ {len(X_train)} records prepared for Feature Store")
    print(f"✓ Saved to {output_path}")

    return X_train


def save_feature_schema(schema):
    """Save feature group schema to docs."""

    output_path = f"{FINAL_PATH}feature_group_schema.json"
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=4)

    print(f"\n✓ Feature schema saved to {output_path}")


if __name__ == "__main__":
    print("Starting Feature Store setup...\n")

    # Define feature group
    schema = define_feature_group()

    # Prepare features
    features_df = prepare_features_for_store()

    # Save schema
    save_feature_schema(schema)

    print("\n--- Feature Store Summary ---")
    print(f"Feature group   : surf-pipeline-features")
    print(f"Total features  : 17")
    print(f"Records ready   : {len(features_df)}")
    print(f"Online store    : Enabled")
    print(f"Offline store   : s3://surf-pipeline-final-agl/feature-store/")

    print("\n✓ Feature Store setup complete!")