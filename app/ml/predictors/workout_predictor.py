"""
Workout Predictor

Loads the trained workout classification model and encoders,
and recommends a list of exercises based on user profile.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd


class WorkoutPredictor:
    """
    Classifies exercises and generates personalized workout plans.
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_DIR = BASE_DIR / "trained_models"
    MODEL_PATH = MODEL_DIR / "workout_model.pkl"

    def __init__(self):
        # Load classification model
        self.model = joblib.load(self.MODEL_PATH)
        
        # Load encoders
        self.type_encoder = joblib.load(self.MODEL_DIR / "Type_encoder.pkl")
        self.bodypart_encoder = joblib.load(self.MODEL_DIR / "BodyPart_encoder.pkl")
        self.equipment_encoder = joblib.load(self.MODEL_DIR / "Equipment_encoder.pkl")
        self.level_encoder = joblib.load(self.MODEL_DIR / "Level_encoder.pkl")

        # Load processed workouts for selection
        self.processed_workouts_path = self.BASE_DIR / "datasets" / "processed" / "workout_processed.csv"
        if self.processed_workouts_path.exists():
            self.workouts_df = pd.read_csv(self.processed_workouts_path)
        else:
            self.workouts_df = None

    def predict_level(self, exercise_type: str, body_part: str, equipment: str) -> str:
        """
        Predict difficulty level of an exercise based on features.
        """
        # Encode inputs, fallback to mode if unseen
        def encode_val(encoder, val):
            try:
                return encoder.transform([val])[0]
            except Exception:
                # Use the mode/first class as fallback
                return encoder.transform([encoder.classes_[0]])[0]

        type_encoded = encode_val(self.type_encoder, exercise_type)
        bodypart_encoded = encode_val(self.bodypart_encoder, body_part)
        equipment_encoded = encode_val(self.equipment_encoder, equipment)

        features = pd.DataFrame(
            [[type_encoded, bodypart_encoded, equipment_encoded]],
            columns=["Type", "BodyPart", "Equipment"]
        )
        pred_class = self.model.predict(features)[0]
        
        return self.level_encoder.inverse_transform([pred_class])[0]

    def recommend_workouts(self, profile, limit=5) -> list:
        """
        Recommend specific exercises based on user's goal and activity level.
        """
        if self.workouts_df is None:
            return ["No workout database available."]

        goal = profile.goal.value.lower()
        activity = profile.activity_level.value.lower()

        # Determine target level based on activity
        if "sedentary" in activity or "lightly" in activity:
            target_level = "Beginner"
        elif "moderately" in activity:
            target_level = "Intermediate"
        else:
            target_level = "Expert"

        # Determine target types based on goal
        if "lose" in goal:
            target_types = ["Cardio", "Plyometrics", "Stretching"]
        elif "gain" in goal:
            target_types = ["Strength", "Powerlifting", "Olympic Weightlifting"]
        else:
            target_types = ["Strength", "Cardio", "Stretching"]

        # Filter database by target types
        candidates = self.workouts_df[self.workouts_df["Type"].isin(target_types)].copy()
        if candidates.empty:
            candidates = self.workouts_df.copy()

        # Classify candidates using the ML model
        # For performance, we pre-encode the columns and batch predict
        def safe_encode(encoder, col_data):
            classes_set = set(encoder.classes_)
            # Map unseen to the default class
            default_val = encoder.classes_[0]
            mapped = col_data.astype(str).apply(lambda x: x if x in classes_set else default_val)
            return encoder.transform(mapped)

        candidates["Type_enc"] = safe_encode(self.type_encoder, candidates["Type"])
        candidates["BodyPart_enc"] = safe_encode(self.bodypart_encoder, candidates["BodyPart"])
        candidates["Equipment_enc"] = safe_encode(self.equipment_encoder, candidates["Equipment"])

        features = candidates[["Type_enc", "BodyPart_enc", "Equipment_enc"]].copy()
        features.columns = ["Type", "BodyPart", "Equipment"]
        predictions = self.model.predict(features)
        candidates["Predicted_Level"] = self.level_encoder.inverse_transform(predictions)

        # Filter by predicted level matching target level
        filtered = candidates[candidates["Predicted_Level"] == target_level].copy()
        if filtered.empty:
            # Fallback if no exact match
            filtered = candidates.copy()

        # Sort by rating if available, or shuffle to be dynamic
        if "Rating" in filtered.columns:
            # Fill na with 0
            filtered["Rating"] = filtered["Rating"].fillna(0)
            filtered = filtered.sort_values(by="Rating", ascending=False)
        else:
            filtered = filtered.sample(frac=1, random_state=42)

        # Select diverse exercises targeting different body parts
        recommended = []
        seen_bodyparts = set()
        
        for _, row in filtered.iterrows():
            bp = row["BodyPart"]
            title = row["Title"]
            eq = row["Equipment"] if pd.notna(row["Equipment"]) else "Body Only"
            
            if bp not in seen_bodyparts:
                seen_bodyparts.add(bp)
                recommended.append(f"{row['Type']}: {title} ({bp}) - Equipment: {eq}")
                
            if len(recommended) >= limit:
                break

        # Fallback to fill the limit if not enough diverse body parts
        if len(recommended) < limit:
            for _, row in filtered.iterrows():
                title = row["Title"]
                bp = row["BodyPart"]
                eq = row["Equipment"] if pd.notna(row["Equipment"]) else "Body Only"
                item = f"{row['Type']}: {title} ({bp}) - Equipment: {eq}"
                if item not in recommended:
                    recommended.append(item)
                if len(recommended) >= limit:
                    break

        return recommended
