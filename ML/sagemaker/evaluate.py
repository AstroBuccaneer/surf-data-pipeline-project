import pandas as pd
import numpy as np
import json
import pickle
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.impute import SimpleImputer

# Paths
FINAL_PATH = "data/final/"
PROCESSED_PATH = "data/processed/"

print("✓ Evaluation script initialized")


def load_model_and_data():
    """Load saved model and test data for evaluation."""

    print("Loading model and test data...")

    # Load best model
    with open(f"{FINAL_PATH}best_model.pkl", "rb") as f:
        model = pickle.load(f)

    # Load model metadata
    with open(f"{FINAL_PATH}model_metadata.json", "r") as f:
        metadata = json.load(f)

    # Load test data
    X_test = pd.read_csv(f"{FINAL_PATH}X_test.csv").values
    y_test = pd.read_csv(f"{FINAL_PATH}y_test.csv").values.ravel()

    # Handle NaN values
    imputer = SimpleImputer(strategy="mean")
    X_test = imputer.fit_transform(X_test)

    # Load feature columns
    with open(f"{FINAL_PATH}feature_cols.json", "r") as f:
        feature_cols = json.load(f)

    print(f"✓ Model loaded      : {metadata['model_name']}")
    print(f"✓ Test samples      : {X_test.shape[0]}")
    print(f"✓ Features          : {X_test.shape[1]}")

    return model, X_test, y_test, feature_cols, metadata


def evaluate_model(model, X_test, y_test, metadata):
    """Run deep evaluation on the trained model."""

    print("\nRunning model evaluation...")

    # Generate predictions
    y_pred = model.predict(X_test)

    # Core metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Additional metrics
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    max_error = np.max(np.abs(y_test - y_pred))

    # Prediction breakdown
    within_10pct = np.sum(np.abs(y_test - y_pred) / y_test < 0.10) / len(y_test) * 100
    within_20pct = np.sum(np.abs(y_test - y_pred) / y_test < 0.20) / len(y_test) * 100
    within_50pct = np.sum(np.abs(y_test - y_pred) / y_test < 0.50) / len(y_test) * 100

    print(f"\n--- Model Evaluation Report ---")
    print(f"Model           : {metadata['model_name']}")
    print(f"RMSE            : {rmse:.4f} meters")
    print(f"MAE             : {mae:.4f} meters")
    print(f"R2 Score        : {r2:.4f}")
    print(f"MAPE            : {mape:.2f}%")
    print(f"Max Error       : {max_error:.4f} meters")
    print(f"\nPrediction Accuracy:")
    print(f"Within 10%      : {within_10pct:.1f}% of predictions")
    print(f"Within 20%      : {within_20pct:.1f}% of predictions")
    print(f"Within 50%      : {within_50pct:.1f}% of predictions")

    evaluation = {
        "model_name": metadata["model_name"],
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "mape": round(mape, 2),
        "max_error": round(max_error, 4),
        "within_10pct": round(within_10pct, 1),
        "within_20pct": round(within_20pct, 1),
        "within_50pct": round(within_50pct, 1)
    }

    return evaluation, y_pred


def evaluate_by_location(model, X_test, y_test, feature_cols):
    """Evaluate model performance broken down by location."""

    print("\nEvaluating by location...")

    # Load test data with location info
    X_test_df = pd.read_csv(f"{FINAL_PATH}X_test.csv")
    y_pred = model.predict(SimpleImputer(strategy="mean").fit_transform(X_test))

    # Identify location columns
    loc_cols = [col for col in X_test_df.columns if col.startswith("loc_")]

    results = []

    for loc_col in loc_cols:
        location_name = loc_col.replace("loc_", "")
        mask = X_test_df[loc_col] == 1

        if mask.sum() == 0:
            continue

        y_true_loc = y_test[mask]
        y_pred_loc = y_pred[mask]

        if len(y_true_loc) == 0:
            continue

        rmse = np.sqrt(mean_squared_error(y_true_loc, y_pred_loc))
        mae = mean_absolute_error(y_true_loc, y_pred_loc)
        r2 = r2_score(y_true_loc, y_pred_loc) if len(y_true_loc) > 1 else None

        results.append({
            "location": location_name,
            "samples": int(mask.sum()),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "r2": round(r2, 4) if r2 is not None else "N/A"
        })

        print(f"{location_name:<20} RMSE: {rmse:.4f}  MAE: {mae:.4f}  R2: {r2:.4f if r2 else 'N/A'}")

    return results


def save_evaluation_report(evaluation, location_results):
    """Save full evaluation report to final folder."""

    report = {
        "overall": evaluation,
        "by_location": location_results
    }

    report_path = f"{FINAL_PATH}evaluation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)

    print(f"\n✓ Evaluation report saved to {report_path}")


if __name__ == "__main__":
    print("Starting model evaluation...\n")

    # Load model and data
    model, X_test, y_test, feature_cols, metadata = load_model_and_data()

    # Run overall evaluation
    evaluation, y_pred = evaluate_model(model, X_test, y_test, metadata)

    # Evaluate by location
    location_results = evaluate_by_location(
        model, X_test, y_test, feature_cols
    )

    # Save evaluation report
    save_evaluation_report(evaluation, location_results)

    print("\n✓ Model evaluation complete!")


