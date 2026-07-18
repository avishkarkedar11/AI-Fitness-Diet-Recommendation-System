"""
Calorie Predictor

Loads the trained calorie prediction model
and predicts daily calorie requirements.
"""

from pathlib import Path

import joblib
import numpy as np


class CaloriePredictor:
    """
    Predict calories using the trained model.
    """

    # ==========================================
    # Paths
    # ==========================================

    BASE_DIR = Path(__file__).resolve().parent.parent

    MODEL_DIR = BASE_DIR / "trained_models"

    MODEL_PATH = MODEL_DIR / "calorie_model.pkl"

    SCALER_PATH = MODEL_DIR / "scaler.pkl"

    GENDER_ENCODER_PATH = (
        MODEL_DIR /
        "Gender_encoder.pkl"
    )

    # ==========================================
    # Initialize
    # ==========================================

    def __init__(self):

        self.model = joblib.load(
            self.MODEL_PATH
        )

        self.scaler = joblib.load(
            self.SCALER_PATH
        )

        self.gender_encoder = joblib.load(
            self.GENDER_ENCODER_PATH
        )

    # ==========================================
    # Prediction
    # ==========================================

    def predict(
        self,
        gender,
        age,
        height,
        weight,
        duration,
        heart_rate,
        body_temp
    ):
        """
        Predict calories burned.

        Parameters
        ----------
        gender : str
        age : int
        height : float
        weight : float
        duration : float
        heart_rate : float
        body_temp : float

        Returns
        -------
        float
        """

        # --------------------------------------
        # Encode Gender
        # --------------------------------------

        gender = self.gender_encoder.transform(
            [gender.lower()]
        )[0]

        # --------------------------------------
        # Feature Vector
        # --------------------------------------

        features = np.array([
            [
                gender,
                age,
                height,
                weight,
                duration,
                heart_rate,
                body_temp
            ]
        ])

        # --------------------------------------
        # Scale Features
        # --------------------------------------

        features = self.scaler.transform(
            features
        )

        # --------------------------------------
        # Predict
        # --------------------------------------

        prediction = self.model.predict(
            features
        )[0]

        return round(
            float(prediction),
            2
        )

    # ==========================================
    # Predict From Profile
    # ==========================================

    def predict_from_profile(
        self,
        profile
    ):
        """
        Predict calories directly
        from a FitnessProfile object.
        """

        return self.predict(

            gender=profile.gender.value,

            age=profile.age,

            height=profile.height_cm,

            weight=profile.weight_kg,

            # Default values until
            # activity tracking module

            duration=45,

            heart_rate=95,

            body_temp=37.0

        )