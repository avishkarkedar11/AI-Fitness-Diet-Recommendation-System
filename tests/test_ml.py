"""
Unit Tests for Machine Learning Models and Predictors
"""

import unittest
from app import create_app
from app.utils.enums import Gender, FitnessGoal, ActivityLevel
from app.ml.predictors.calorie_predictor import CaloriePredictor
from app.ml.predictors.workout_predictor import WorkoutPredictor
from app.ml.predictors.diet_predictor import DietPredictor
from app.ml.predictors.progress_predictor import ProgressPredictor


class ProfileMock:
    def __init__(self):
        self.gender = Gender.MALE
        self.age = 25
        self.height_cm = 180.0
        self.weight_kg = 80.0
        self.target_weight_kg = 75.0
        self.goal = FitnessGoal.LOSE_WEIGHT
        self.activity_level = ActivityLevel.MODERATELY_ACTIVE
        self.workout_hours = 1.5
        self.sleep_hours = 8.0
        self.daily_steps = 10000
        self.dietary_preference = "Vegetarian"
        self.medical_conditions = "None"


class TestMLPredictors(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.profile = ProfileMock()

    def tearDown(self):
        self.ctx.pop()

    def test_calorie_predictor(self):
        predictor = CaloriePredictor()
        calories = predictor.predict_from_profile(self.profile)
        self.assertIsInstance(calories, float)
        self.assertTrue(calories > 0)

    def test_workout_predictor(self):
        predictor = WorkoutPredictor()
        
        # Test level prediction
        level = predictor.predict_level("Cardio", "Abdominals", "Body Only")
        self.assertIn(level, ["Beginner", "Intermediate", "Expert"])

        # Test workout recommendations list
        workouts = predictor.recommend_workouts(self.profile, limit=3)
        self.assertEqual(len(workouts), 3)
        for workout in workouts:
            self.assertIsInstance(workout, str)
            self.assertIn(":", workout)

    def test_diet_predictor(self):
        predictor = DietPredictor()
        
        nutrition_targets = {
            "target_calories": 2200,
            "protein_g": 140,
            "carbs_g": 250,
            "fat_g": 70,
            "water_liters": 3.0
        }
        
        # Test daily meal recommendation structure
        meals = predictor.recommend_meals(self.profile, nutrition_targets, limit=2)
        
        self.assertIn("breakfast", meals)
        self.assertIn("lunch", meals)
        self.assertIn("dinner", meals)
        self.assertIn("plan", meals)
        
        self.assertEqual(len(meals["breakfast"]), 2)
        self.assertEqual(len(meals["lunch"]), 2)
        self.assertEqual(len(meals["dinner"]), 2)
        self.assertEqual(len(meals["plan"]), 3)  # Flat plan list

    def test_progress_predictor(self):
        predictor = ProgressPredictor()
        
        history_weights = [82.0, 81.5, 81.2, 80.8, 80.5]
        dates = ["10 Jul", "11 Jul", "12 Jul", "13 Jul", "14 Jul"]
        
        forecast = predictor.forecast_weight(history_weights, dates, days_ahead=7)
        
        self.assertEqual(len(forecast), 7)
        for day in forecast:
            self.assertIn("date", day)
            self.assertIn("weight", day)
            self.assertIsInstance(day["weight"], float)
            self.assertTrue(30.0 < day["weight"] < 250.0)


if __name__ == "__main__":
    unittest.main()
