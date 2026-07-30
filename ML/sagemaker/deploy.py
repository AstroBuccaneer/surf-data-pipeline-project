import boto3
import json
import pickle
import os
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from datetime import datetime

# Paths
FINAL_PATH = "data/final/"

# AWS config
REGION = "us-east-1"
S3_BUCKET = "surf-pipeline-final-agl"

# SageMaker client
sagemaker = boto3.client("sagemaker", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)

print("✓ Deploy script initialized")

def upload_model_to_s3():
    """Upload trained model to S3 for SageMaker deployment."""

    print("Uploading model to S3...")

    # Upload model file
    model_path = f"{FINAL_PATH}best_model.pkl"
    s3_key = "models/best_model.pkl"

    s3.upload_file(
        model_path,
        S3_BUCKET,
        s3_key
    )

    print(f"✓ Model uploaded to s3://{S3_BUCKET}/{s3_key}")

    # Upload model metadata
    metadata_path = f"{FINAL_PATH}model_metadata.json"
    s3_metadata_key = "models/model_metadata.json"

    s3.upload_file(
        metadata_path,
        S3_BUCKET,
        s3_metadata_key
    )

    print(f"✓ Metadata uploaded to s3://{S3_BUCKET}/{s3_metadata_key}")

    # Upload evaluation report
    eval_path = f"{FINAL_PATH}evaluation_report.json"
    s3_eval_key = "models/evaluation_report.json"

    s3.upload_file(
        eval_path,
        S3_BUCKET,
        s3_eval_key
    )

    print(f"✓ Evaluation report uploaded to s3://{S3_BUCKET}/{s3_eval_key}")

    return f"s3://{S3_BUCKET}/models/best_model.pkl"


def simulate_endpoint_prediction():
    """Simulate SageMaker endpoint prediction locally."""

    print("\nSimulating endpoint predictions...")

    # Load model and feature cols
    with open(f"{FINAL_PATH}best_model.pkl", "rb") as f:
        model = pickle.load(f)

    with open(f"{FINAL_PATH}feature_cols.json", "r") as f:
        feature_cols = json.load(f)

    # Load model metadata
    with open(f"{FINAL_PATH}model_metadata.json", "r") as f:
        metadata = json.load(f)

    # Simulate prediction for each location next month
    locations = {
        "pensacola_beach": {"loc_pensacola_beach": 1, "loc_cocoa_beach": 0,
                            "loc_huntington_beach": 0, "loc_waikiki": 0},
        "cocoa_beach":     {"loc_pensacola_beach": 0, "loc_cocoa_beach": 1,
                            "loc_huntington_beach": 0, "loc_waikiki": 0},
        "huntington_beach":{"loc_pensacola_beach": 0, "loc_cocoa_beach": 0,
                            "loc_huntington_beach": 1, "loc_waikiki": 0},
        "waikiki":         {"loc_pensacola_beach": 0, "loc_cocoa_beach": 0,
                            "loc_huntington_beach": 0, "loc_waikiki": 1}
    }

    # Use average feature values as baseline
    X_test = pd.read_csv(f"{FINAL_PATH}X_test.csv")
    imputer = SimpleImputer(strategy="mean")
    X_test_imputed = imputer.fit_transform(X_test)
    baseline = np.mean(X_test_imputed, axis=0)

    print(f"\n--- Surf Score Predictions for Next Month ---")
    print(f"{'Location':<20} {'Predicted Wave (m)':<22} {'Predicted Wave (ft)':<22} {'Surfable?'}")
    print("-" * 80)

    predictions = []

    for location, loc_flags in locations.items():
        # Build feature vector
        feature_vector = baseline.copy()

        # Set location flags
        for i, col in enumerate(feature_cols):
            if col in loc_flags:
                feature_vector[i] = loc_flags[col]

        # Predict
        pred_m = model.predict([feature_vector])[0]
        pred_ft = round(pred_m * 3.28084, 2)
        surfable = "Yes" if pred_m >= 1.5 else "No"

        predictions.append({
            "location": location,
            "predicted_wave_m": round(pred_m, 2),
            "predicted_wave_ft": pred_ft,
            "surfable": surfable,
            "pct_of_nazare": round(pred_m / 26.2 * 100, 2)
        })

        print(f"{location:<20} {pred_m:<22.2f} {pred_ft:<22.2f} {surfable}")

    return predictions


def save_predictions(predictions):
    """Save endpoint predictions to final folder."""

    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "model": "Random Forest",
        "predictions": predictions
    }

    pred_path = f"{FINAL_PATH}surf_predictions.json"
    with open(pred_path, "w") as f:
        json.dump(output, f, indent=4)

    print(f"\n✓ Predictions saved to {pred_path}")

    # Upload predictions to S3
    s3.upload_file(
        pred_path,
        S3_BUCKET,
        "models/surf_predictions.json"
    )

    print(f"✓ Predictions uploaded to s3://{S3_BUCKET}/models/surf_predictions.json")


if __name__ == "__main__":
    print("Starting SageMaker deployment simulation...\n")

    # Upload model to S3
    model_s3_path = upload_model_to_s3()

    # Simulate endpoint predictions
    predictions = simulate_endpoint_prediction()

    # Save predictions
    save_predictions(predictions)

    print("\n--- Deployment Summary ---")
    print(f"Model location  : s3://{S3_BUCKET}/models/best_model.pkl")
    print(f"Predictions     : s3://{S3_BUCKET}/models/surf_predictions.json")
    print("\n✓ Deployment simulation complete!")


