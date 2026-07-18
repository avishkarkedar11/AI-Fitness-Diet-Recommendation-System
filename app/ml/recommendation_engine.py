"""
Recommendation Engine

Provides a central driver to preprocess datasets and train all four machine learning models:
1. Calorie Prediction Model (Regression)
2. Workout Recommendation Model (Classification)
3. Diet Recommendation Model (Content-Based Filtering)
4. Progress Tracker Model (LSTM Time Series)
"""

from app.ml.training.train_calorie_model import CalorieModelTrainer
from app.ml.training.train_workout_model import WorkoutModelTrainer
from app.ml.training.train_diet_model import DietModelTrainer
from app.ml.training.train_progress_model import ProgressModelTrainer


class RecommendationEngine:
    """
    Orchestrates training for all AI models.
    """

    @classmethod
    def train_all_models(cls):
        """
        Train all models sequentially.
        """
        print("Starting training suite for all AI Fitness & Diet models...\n")

        # 1. Calorie Model
        print("[1/4] Training Calorie Prediction Model (Regression)...")
        from app.ml.preprocessing import DataPreprocessor
        DataPreprocessor.preprocess("calories.csv", "calories_processed.csv")
        CalorieModelTrainer.train()

        # 2. Workout Model
        print("\n[2/4] Training Workout Recommendation Model (Classification)...")
        WorkoutModelTrainer.train()

        # 3. Diet Model
        print("\n[3/4] Training Diet Recommendation Model (Content-Based)...")
        DietModelTrainer.train()

        # 4. Progress Model
        print("\n[4/4] Training Progress Tracker Model (LSTM Time Series)...")
        ProgressModelTrainer.train()

        print("\nAI Model Training Suite Completed successfully!")
