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

        gender_str = str(getattr(profile, 'gender', '')).upper()

        if "MALE" in gender_str and "FEMALE" not in gender_str:

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
            1.20
        )

        tdee = bmr * factor

        # --------------------------------------
        # Workout Adjustment
        # --------------------------------------

        workout_hours = profile.workout_hours or 0

        tdee += workout_hours * 120

        # --------------------------------------
        # Daily Steps Adjustment
        # --------------------------------------

        steps = profile.daily_steps or 0

        if steps >= 12000:
            tdee += 250

        elif steps >= 10000:
            tdee += 180

        elif steps >= 8000:
            tdee += 120

        elif steps >= 5000:
            tdee += 60

        return round(tdee)

    # ==========================================
    # Target Calories
    # ==========================================

    @classmethod
    def target_calories(cls, profile):
        """
        Calculate calories according to goal.
        """

        calories = cls.calculate_tdee(profile)
        goal_str = str(getattr(profile, 'goal', '')).upper()

        if "LOSE" in goal_str:

            calories -= 500

        elif "GAIN" in goal_str:

            calories += 400

        elif "MAINTAIN" in goal_str:

            calories += 0

        return max(round(calories), 1200)

    # ==========================================
    # Water Intake
    # ==========================================

    @staticmethod
    def water_intake(profile):
        """
        Daily water intake in liters.
        """

        if profile and profile.water_intake_liters is not None:
            return round(profile.water_intake_liters, 1)

        liters = (profile.weight_kg * 35) / 1000

        workout = profile.workout_hours or 0

        liters += workout * 0.5

        return round(liters, 1)

    # ==========================================
    # Macronutrients
    # ==========================================

    @classmethod
    def macronutrients(cls, profile):
        """
        Calculate daily macros.
        """

        calories = cls.target_calories(profile)

        # Protein (2 g/kg)

        protein = profile.weight_kg * 2

        # Fat (25%)

        fats = (calories * 0.25) / 9

        # Remaining Calories → Carbs

        remaining = calories - (
            protein * 4 +
            fats * 9
        )

        carbs = remaining / 4

        return {
            "protein_g": round(protein),
            "carbs_g": round(carbs),
            "fat_g": round(fats)
        }

    # ==========================================
    # Complete Nutrition Report
    # ==========================================

    @classmethod
    def nutrition_report(cls, profile):
        """
        Generate complete nutrition report.
        """

        bmr = round(
            cls.calculate_bmr(profile)
        )

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