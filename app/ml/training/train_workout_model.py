"""
Train Workout Recommendation (Classification) Model

Trains a Random Forest Classifier to predict the difficulty level of workouts.
"""

from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from app.ml.preprocessing import DataPreprocessor


class WorkoutModelTrainer:
    """
    Handles workout classification model training.
    """

    MODEL_NAME = "workout_model.pkl"

    @classmethod
    def train(cls):
        print("=" * 60)
        print("Preprocessing raw workout dataset...")
        print("=" * 60)

        # Preprocess the dataset
        DataPreprocessor.preprocess("workout.csv", "workout_processed.csv")
        
        # Load the processed dataset
        processed_dir = Path(__file__).resolve().parent.parent / "datasets" / "processed"
        df = pd.read_csv(processed_dir / "workout_processed.csv")

        print("Dataset preprocessed and loaded.")

        # ==========================================
        # Feature Engineering (Encoders)
        # ==========================================
        model_dir = Path(__file__).resolve().parent.parent / "trained_models"
        model_dir.mkdir(exist_ok=True)

        categorical_cols = ["Type", "BodyPart", "Equipment"]
        encoders = {}

        for col in categorical_cols:
            le = LabelEncoder()
            # Handle missing or unseen values gracefully
            df[col] = df[col].astype(str)
            df[col] = le.fit_transform(df[col])
            encoders[col] = le
            joblib.dump(le, model_dir / f"{col}_encoder.pkl")
            print(f"Saved encoder for {col}")

        # Encode target variable
        target_encoder = LabelEncoder()
        df["Level"] = target_encoder.fit_transform(df["Level"])
        joblib.dump(target_encoder, model_dir / "Level_encoder.pkl")
        print("Saved encoder for Level")

        # Prepare X and y
        X = df[categorical_cols]
        y = df["Level"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # ==========================================
        # Model Training
        # ==========================================
        print("\nTraining Random Forest Classifier...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        print("Training completed.")

        # ==========================================
        # Evaluation
        # ==========================================
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        print("\nModel Evaluation")
        print("-" * 40)
        print(f"Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(
            y_test, 
            predictions, 
            target_names=target_encoder.classes_
        ))

        # Save model
        model_path = model_dir / cls.MODEL_NAME
        joblib.dump(model, model_path)
        print(f"\nModel saved successfully at: {model_path}")
        print("=" * 60)

        return model


if __name__ == "__main__":
    WorkoutModelTrainer.train()
