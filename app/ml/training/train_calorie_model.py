"""
Train Calorie Prediction Model

Trains a Random Forest Regressor for
predicting daily calorie requirements.
"""

from pathlib import Path

import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from app.ml.feature_engineering import FeatureEngineering


class CalorieModelTrainer:
    """
    Handles calorie model training.
    """

    MODEL_NAME = "calorie_model.pkl"

    # ==========================================
    # Train Model
    # ==========================================

    @classmethod
    def train(cls):
        """
        Train calorie prediction model.
        """

        print("=" * 60)
        print("Loading processed dataset...")
        print("=" * 60)

        X_train, X_test, y_train, y_test = (
            FeatureEngineering.prepare_dataset(
                dataset_name="calories_processed.csv",
                target_column="Calories",
                categorical_columns=["Gender"]
            )
        )

        print("Dataset loaded successfully.")

        # ======================================
        # Model
        # ======================================

        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            random_state=42,
            n_jobs=-1
        )

        print("\nTraining model...")

        model.fit(
            X_train,
            y_train
        )

        print("Training completed.")

        # ======================================
        # Prediction
        # ======================================

        predictions = model.predict(
            X_test
        )

        # ======================================
        # Evaluation
        # ======================================

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        mse = mean_squared_error(
            y_test,
            predictions
        )

        rmse = mse ** 0.5

        r2 = r2_score(
            y_test,
            predictions
        )

        print("\nModel Evaluation")
        print("-" * 40)

        print(f"MAE  : {mae:.2f}")
        print(f"RMSE : {rmse:.2f}")
        print(f"R²   : {r2:.4f}")

        # ======================================
        # Save Model
        # ======================================

        model_dir = (
            Path(__file__)
            .resolve()
            .parent.parent
            / "trained_models"
        )

        model_dir.mkdir(
            exist_ok=True
        )

        model_path = (
            model_dir /
            cls.MODEL_NAME
        )

        joblib.dump(
            model,
            model_path
        )

        print("\nModel Saved Successfully")
        print(model_path)

        return model


# ==========================================
# Run Script
# ==========================================

if __name__ == "__main__":

    CalorieModelTrainer.train()
    