import pandas as pd
import numpy as np
import json
import os
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.impute import SimpleImputer

# Paths
FINAL_PATH = "data/final/"

print("✓ Training script initialized")

def load_training_data():
    """Load preprocessed training and test data."""

    print("Loading training data...")

    X_train = pd.read_csv(f"{FINAL_PATH}X_train.csv").values
    X_test = pd.read_csv(f"{FINAL_PATH}X_test.csv").values
    y_train = pd.read_csv(f"{FINAL_PATH}y_train.csv").values.ravel()
    y_test = pd.read_csv(f"{FINAL_PATH}y_test.csv").values.ravel()

    # Handle NaN values by filling with column mean
    imputer = SimpleImputer(strategy="mean")
    X_train = imputer.fit_transform(X_train)
    X_test = imputer.transform(X_test)

    with open(f"{FINAL_PATH}feature_cols.json", "r") as f:
        feature_cols = json.load(f)

    print(f"✓ Training samples  : {X_train.shape[0]}")
    print(f"✓ Test samples      : {X_test.shape[0]}")
    print(f"✓ Features          : {X_train.shape[1]}")

    return X_train, X_test, y_train, y_test, feature_cols


def train_models(X_train, X_test, y_train, y_test):
    """Train multiple models and compare performance."""

    print("\nTraining models...")

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
    }

    results = {}

    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")

        # Train
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)

        # Evaluate
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        results[model_name] = {
            "model": model,
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "r2": round(r2, 4),
            "predictions": y_pred.tolist()
        }

        print(f"✓ RMSE : {rmse:.4f}")
        print(f"✓ MAE  : {mae:.4f}")
        print(f"✓ R2   : {r2:.4f}")

    return results

def select_and_save_best_model(results, feature_cols):
    """Select best model based on RMSE and save it."""

    print("\nSelecting best model...")

    # Select model with lowest RMSE
    best_model_name = min(
        results,
        key=lambda x: results[x]["rmse"]
    )
    best_model = results[best_model_name]

    print(f"\n--- Model Comparison ---")
    for name, result in results.items():
        marker = "← BEST" if name == best_model_name else ""
        print(f"{name:<25} RMSE: {result['rmse']:.4f}  MAE: {result['mae']:.4f}  R2: {result['r2']:.4f} {marker}")

    # Save best model
    model_path = f"{FINAL_PATH}best_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(best_model["model"], f)

    # Save model metadata
    metadata = {
        "model_name": best_model_name,
        "rmse": best_model["rmse"],
        "mae": best_model["mae"],
        "r2": best_model["r2"],
        "feature_cols": feature_cols,
        "training_samples": 513,
        "test_samples": 129
    }

    metadata_path = f"{FINAL_PATH}model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"\n✓ Best model saved to {model_path}")
    print(f"✓ Model metadata saved to {metadata_path}")

    return best_model_name, best_model["model"]


def get_feature_importance(model, feature_cols, model_name):
    """Print feature importance for tree based models."""

    if hasattr(model, "feature_importances_"):
        print(f"\n--- Feature Importance ({model_name}) ---")
        importance_df = pd.DataFrame({
            "feature": feature_cols,
            "importance": model.feature_importances_
        }).sort_values("importance", ascending=False)

        for _, row in importance_df.head(10).iterrows():
            bar = "█" * int(row["importance"] * 100)
            print(f"{row['feature']:<30} {bar} {row['importance']:.4f}")

        return importance_df
    return None


if __name__ == "__main__":
    print("Starting SageMaker model training...\n")

    # Load training data
    X_train, X_test, y_train, y_test, feature_cols = load_training_data()

    # Train all models
    results = train_models(X_train, X_test, y_train, y_test)

    # Select and save best model
    best_model_name, best_model = select_and_save_best_model(
        results, feature_cols
    )

    # Show feature importance
    get_feature_importance(best_model, feature_cols, best_model_name)

    print("\n✓ Model training complete!")

