import pandas as pd
import numpy as np
import pickle
import json
import os
from sklearn.impute import SimpleImputer

# Paths
FINAL_PATH = "data/final/"
PROCESSED_PATH = "data/processed/"

print("✓ SHAP analysis initialized")


def load_model_and_data():
    """Load trained model and test data for explainability analysis."""

    print("Loading model and data...")

    # Load model
    with open(f"{FINAL_PATH}best_model.pkl", "rb") as f:
        model = pickle.load(f)

    # Load metadata
    with open(f"{FINAL_PATH}model_metadata.json", "r") as f:
        metadata = json.load(f)

    # Load feature columns
    with open(f"{FINAL_PATH}feature_cols.json", "r") as f:
        feature_cols = json.load(f)

    # Load test data
    X_test = pd.read_csv(f"{FINAL_PATH}X_test.csv")

    # Handle NaN values
    imputer = SimpleImputer(strategy="mean")
    X_test_imputed = imputer.fit_transform(X_test)

    print(f"✓ Model loaded      : {metadata['model_name']}")
    print(f"✓ Test samples      : {X_test_imputed.shape[0]}")
    print(f"✓ Features          : {len(feature_cols)}")

    return model, X_test_imputed, feature_cols, metadata


def calculate_feature_importance(model, feature_cols):
    """Calculate and display feature importance."""

    print("\nCalculating feature importance...")

    if not hasattr(model, "feature_importances_"):
        print("Model does not support feature importance")
        return None

    importance_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    print("\n--- Feature Importance Rankings ---")
    for i, row in importance_df.iterrows():
        bar = "█" * int(row["importance"] * 100)
        print(f"{row['feature']:<30} {bar} {row['importance']:.4f}")

    return importance_df


def analyze_location_predictions(model, X_test, feature_cols):
    """Analyze predictions broken down by location."""

    print("\nAnalyzing predictions by location...")

    X_test_df = pd.read_csv(f"{FINAL_PATH}X_test.csv")
    imputer = SimpleImputer(strategy="mean")
    X_test_imputed = imputer.fit_transform(X_test_df)
    predictions = model.predict(X_test_imputed)

    loc_cols = [col for col in X_test_df.columns if col.startswith("loc_")]

    print("\n--- Prediction Analysis by Location ---")
    for loc_col in loc_cols:
        location = loc_col.replace("loc_", "")
        mask = X_test_df[loc_col] == 1

        if mask.sum() == 0:
            continue

        loc_preds = predictions[mask]
        print(f"\n{location}:")
        print(f"  Samples        : {mask.sum()}")
        print(f"  Avg predicted  : {loc_preds.mean():.2f}m")
        print(f"  Max predicted  : {loc_preds.max():.2f}m")
        print(f"  Min predicted  : {loc_preds.min():.2f}m")


def generate_explainability_report(importance_df, metadata):
    """Generate and save explainability report."""

    print("\nGenerating explainability report...")

    report = {
        "model_name": metadata["model_name"],
        "r2_score": metadata["r2"],
        "rmse": metadata["rmse"],
        "feature_importance": importance_df.to_dict(orient="records"),
        "top_3_features": importance_df.head(3)["feature"].tolist(),
        "interpretation": {
            "most_important": importance_df.iloc[0]["feature"],
            "least_important": importance_df.iloc[-1]["feature"],
            "summary": f"The model explains {metadata['r2']*100:.1f}% of wave height variance. "
                      f"The most important predictor is {importance_df.iloc[0]['feature']} "
                      f"with {importance_df.iloc[0]['importance']*100:.1f}% importance."
        }
    }

    output_path = f"{FINAL_PATH}explainability_report.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=4)

    print(f"✓ Explainability report saved to {output_path}")
    return report


if __name__ == "__main__":
    print("Starting SHAP analysis...\n")

    # Load model and data
    model, X_test, feature_cols, metadata = load_model_and_data()

    # Calculate feature importance
    importance_df = calculate_feature_importance(model, feature_cols)

    # Analyze by location
    analyze_location_predictions(model, X_test, feature_cols)

    # Generate report
    if importance_df is not None:
        report = generate_explainability_report(importance_df, metadata)

        print("\n--- Explainability Summary ---")
        print(f"Top feature     : {report['interpretation']['most_important']}")
        print(f"Top 3 features  : {report['top_3_features']}")
        print(f"Model R2        : {report['r2_score']}")
        print(f"\n{report['interpretation']['summary']}")

    print("\n✓ SHAP analysis complete!")