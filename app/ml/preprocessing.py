"""
Preprocessing Module

Provides reusable utilities for preprocessing
machine learning datasets.

Responsibilities:
- Load datasets
- Validate dataset paths
- Handle missing values
- Remove duplicates
- Clean string columns
- Save processed datasets
"""

from pathlib import Path

import pandas as pd


class DataPreprocessor:
    """
    Generic preprocessing class
    for all ML datasets.
    """

    # ==========================================
    # Paths
    # ==========================================

    BASE_DIR = Path(__file__).resolve().parent

    RAW_DATASET_DIR = (
        BASE_DIR /
        "datasets" /
        "raw"
    )

    PROCESSED_DATASET_DIR = (
        BASE_DIR /
        "datasets" /
        "processed"
    )

    # ==========================================
    # Load Dataset
    # ==========================================

    @classmethod
    def load_dataset(cls, filename: str):
        """
        Load dataset from raw folder.

        Parameters
        ----------
        filename : str

        Returns
        -------
        pandas.DataFrame
        """

        file_path = (
            cls.RAW_DATASET_DIR /
            filename
        )

        if not file_path.exists():

            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        return pd.read_csv(file_path)

    # ==========================================
    # Clean Dataset
    # ==========================================

    @staticmethod
    def clean_dataframe(df):
        """
        Clean dataframe.

        Steps:
        - Remove duplicates
        - Fill missing values
        - Strip whitespace
        """

        # Remove duplicate rows

        df = df.drop_duplicates()

        # Strip spaces

        object_columns = (
            df.select_dtypes(
                include="object"
            ).columns
        )

        for column in object_columns:

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
            )

        # Fill missing values

        for column in df.columns:

            if (
                df[column]
                .dtype == "object"
            ):

                mode = (
                    df[column]
                    .mode()
                )

                if not mode.empty:

                    df[column] = (
                        df[column]
                        .fillna(mode[0])
                    )

            else:

                df[column] = (
                    df[column]
                    .fillna(
                        df[column].median()
                    )
                )

        return df

    # ==========================================
    # Save Dataset
    # ==========================================

    @classmethod
    def save_processed_dataset(
        cls,
        dataframe,
        filename
    ):
        """
        Save cleaned dataset.
        """

        cls.PROCESSED_DATASET_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = (
            cls.PROCESSED_DATASET_DIR /
            filename
        )

        dataframe.to_csv(
            output_path,
            index=False
        )

        return output_path

    # ==========================================
    # Complete Pipeline
    # ==========================================

    @classmethod
    def preprocess(
        cls,
        raw_filename,
        processed_filename
    ):
        """
        Full preprocessing pipeline.

        Returns
        -------
        pandas.DataFrame
        """

        dataframe = cls.load_dataset(
            raw_filename
        )

        dataframe = cls.clean_dataframe(
            dataframe
        )

        cls.save_processed_dataset(
            dataframe,
            processed_filename
        )

        return dataframe
    