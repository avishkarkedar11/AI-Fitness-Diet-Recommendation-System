"""
Feature Engineering Module

Provides reusable feature engineering utilities
for machine learning models.

Responsibilities:
- Load processed datasets
- Encode categorical features
- Scale numerical features
- Split dataset
- Save encoder & scaler
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    LabelEncoder,
    StandardScaler
)


class FeatureEngineering:
    """
    Generic Feature Engineering Class.
    """

    # ==========================================
    # Paths
    # ==========================================

    BASE_DIR = Path(__file__).resolve().parent

    DATASET_DIR = (
        BASE_DIR /
        "datasets" /
        "processed"
    )

    MODEL_DIR = (
        BASE_DIR /
        "trained_models"
    )

    # ==========================================
    # Load Dataset
    # ==========================================

    @classmethod
    def load_dataset(cls, filename):
        """
        Load processed dataset.
        """

        file_path = (
            cls.DATASET_DIR /
            filename
        )

        return pd.read_csv(file_path)

    # ==========================================
    # Encode Categorical Columns
    # ==========================================

    @classmethod
    def encode_features(
        cls,
        dataframe,
        categorical_columns
    ):
        """
        Encode categorical columns.
        """

        encoders = {}

        for column in categorical_columns:

            encoder = LabelEncoder()

            dataframe[column] = encoder.fit_transform(
                dataframe[column]
            )

            encoders[column] = encoder

        return dataframe, encoders

    # ==========================================
    # Scale Numerical Columns
    # ==========================================

    @staticmethod
    def scale_features(
        X_train,
        X_test
    ):
        """
        Scale numerical features.
        """

        scaler = StandardScaler()

        X_train = scaler.fit_transform(
            X_train
        )

        X_test = scaler.transform(
            X_test
        )

        return (
            X_train,
            X_test,
            scaler
        )

    # ==========================================
    # Train/Test Split
    # ==========================================

    @staticmethod
    def split_dataset(
        dataframe,
        target_column,
        test_size=0.2,
        random_state=42
    ):
        """
        Split dataset.
        """
        drop_cols = [target_column]
        if "User_ID" in dataframe.columns:
            drop_cols.append("User_ID")
        if "Unnamed: 0" in dataframe.columns:
            drop_cols.append("Unnamed: 0")

        X = dataframe.drop(
            columns=drop_cols
        )

        y = dataframe[target_column]

        return train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state
        )

    # ==========================================
    # Save Objects
    # ==========================================

    @classmethod
    def save_object(
        cls,
        obj,
        filename
    ):
        """
        Save encoder/scaler/model.
        """

        cls.MODEL_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            obj,
            cls.MODEL_DIR / filename
        )

    # ==========================================
    # Complete Pipeline
    # ==========================================

    @classmethod
    def prepare_dataset(
        cls,
        dataset_name,
        target_column,
        categorical_columns=None
    ):
        """
        Complete feature engineering pipeline.
        """

        dataframe = cls.load_dataset(
            dataset_name
        )

        encoders = {}

        if categorical_columns:

            dataframe, encoders = cls.encode_features(
                dataframe,
                categorical_columns
            )

            for column, encoder in encoders.items():

                cls.save_object(
                    encoder,
                    f"{column}_encoder.pkl"
                )

        X_train, X_test, y_train, y_test = (
            cls.split_dataset(
                dataframe,
                target_column
            )
        )

        X_train, X_test, scaler = (
            cls.scale_features(
                X_train,
                X_test
            )
        )

        cls.save_object(
            scaler,
            "scaler.pkl"
        )

        return (
            X_train,
            X_test,
            y_train,
            y_test
        )