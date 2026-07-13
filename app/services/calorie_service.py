"""
Calorie Service

Calculates:
- BMR
- TDEE
- Target Calories
- Macronutrients
- Water Intake
"""

from app.utils.enums import (
    Gender,
    FitnessGoal,
    ActivityLevel,
)


class CalorieService:
    """
    Handles calorie and nutrition calculations.
    """

    # ==========================================
    # Activity Multipliers
    # ==========================================

    ACTIVITY_FACTORS = {
        ActivityLevel.SEDENTARY: 1.20,
        ActivityLevel.LIGHTLY_ACTIVE: 1.375,
        ActivityLevel.MODERATELY_ACTIVE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725,
        ActivityLevel.EXTREMELY_ACTIVE: 1.90,
    }

    # ==========================================
    # BMR
    # ==========================================

    @staticmethod
    def calculate_bmr(profile):
        """
        Calculate Basal Metabolic Rate
        using the Mifflin-St Jeor Equation.
        """

        if profile.gender == Gender.MALE:

            return (
                10 * profile.weight_kg
                + 6.25 * profile.height_cm
                - 5 * profile.age
                + 5
            )

        return (
            10 * profile.weight_kg
            + 6.25 * profile.height_cm
            - 5 * profile.age
            - 161
        )

    # ==========================================
    # TDEE
    # ==========================================

    @classmethod
    def calculate_tdee(cls, profile):
        """
        Calculate Total Daily Energy Expenditure.
        """

        bmr = cls.calculate_bmr(profile)

        factor = cls.ACTIVITY_FACTORS.get(
            profile.activity_level,
            1.2
        )

        return round(bmr * factor)

    # ==========================================
    # Target Calories
    # ==========================================

    @classmethod
    def target_calories(cls, profile):
        """
        Calculate calories based on fitness goal.
        """

        calories = cls.calculate_tdee(profile)

        if profile.goal == FitnessGoal.LOSE_WEIGHT:
            calories -= 500

        elif profile.goal == FitnessGoal.GAIN_WEIGHT:
            calories += 400

        return max(calories, 1200)

    # ==========================================
    # Water Intake
    # ==========================================

    @staticmethod
    def water_intake(profile):
        """
        Daily water intake in liters.
        Formula:
        35 ml × body weight
        """

        liters = (profile.weight_kg * 35) / 1000

        return round(liters, 1)

    # ==========================================
    # Macronutrients
    # ==========================================

    @classmethod
    def macronutrients(cls, profile):
        """
        Calculate Protein, Carbs and Fats.
        """

        calories = cls.target_calories(profile)

        # Protein
        protein = profile.weight_kg * 2

        # Fat
        fats = (calories * 0.25) / 9

        # Remaining Calories
        remaining = calories - (
            protein * 4 +
            fats * 9
        )

        carbs = remaining / 4

        return {
            "protein_g": round(protein),
            "carbs_g": round(carbs),
            "fat_g": round(fats),
        }

    # ==========================================
    # Complete Nutrition Report
    # ==========================================

    @classmethod
    def nutrition_report(cls, profile):
        """
        Returns complete nutrition information.
        """

        bmr = round(cls.calculate_bmr(profile))
        tdee = cls.calculate_tdee(profile)
        calories = cls.target_calories(profile)

        macros = cls.macronutrients(profile)

        return {
            "bmr": bmr,
            "tdee": tdee,
            "target_calories": calories,
            "water_liters": cls.water_intake(profile),
            **macros
        }