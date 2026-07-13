"""
BMI Service

Provides Body Mass Index calculations.
"""


class BMIService:
    """
    Handles BMI calculations.
    """

    @staticmethod
    def calculate(weight_kg: float, height_cm: float):
        """
        Calculate BMI.

        Returns:
            float | None
        """

        if not weight_kg or not height_cm:
            return None

        height_m = height_cm / 100

        bmi = weight_kg / (height_m ** 2)

        return round(bmi, 2)

    @staticmethod
    def category(bmi: float):
        """
        Return BMI category.
        """

        if bmi is None:
            return "Unknown"

        if bmi < 18.5:
            return "Underweight"

        elif bmi < 25:
            return "Normal"

        elif bmi < 30:
            return "Overweight"

        return "Obese"