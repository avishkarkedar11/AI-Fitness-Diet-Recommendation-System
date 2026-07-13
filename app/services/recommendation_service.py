"""
Recommendation Service

Generates personalized fitness and diet recommendations.
"""

from app.extensions import db
from app.models.recommendation import SavedRecommendation
from app.services.profile_service import ProfileService
from app.services.bmi_service import BMIService
from app.services.calorie_service import CalorieService
from app.services.progress_service import ProgressService


class RecommendationService:
    """
    Generates personalized workout and diet recommendations.
    """

    @staticmethod
    def generate(user_id):
        """
        Generate recommendation for a user.
        """

        profile = ProfileService.get_profile(user_id)

        if not profile:
            return None

        latest_progress = ProgressService.latest(user_id)

        current_weight = (
            latest_progress.weight_kg
            if latest_progress
            else profile.weight_kg
        )

        # Calculate BMI (used only for workout logic)
        bmi = BMIService.calculate(
            current_weight,
            profile.height_cm
        )

        # Nutrition Report
        nutrition = CalorieService.nutrition_report(profile)

        # Workout & Diet
        workout = RecommendationService.workout_plan(
            profile.goal,
            bmi
        )

        diet = RecommendationService.diet_plan(
            profile.goal
        )

        recommendation = SavedRecommendation(

            user_id=user_id,

            workout_plan={
                "plan": workout
            },

            diet_plan={
                "plan": diet
            },

            daily_calories=nutrition["target_calories"],

            protein_g=nutrition["protein_g"],

            carbs_g=nutrition["carbs_g"],

            fats_g=nutrition["fat_g"]

        )

        db.session.add(recommendation)
        db.session.commit()

        return recommendation

    # =====================================================
    # Workout Recommendation
    # =====================================================

    @staticmethod
    def workout_plan(goal, bmi):

        goal = str(goal).lower()

        if "lose" in goal:

            return (
                "45 min Cardio\n"
                "30 min Strength Training\n"
                "10,000 Steps Daily"
            )

        elif "gain" in goal:

            return (
                "60 min Weight Training\n"
                "Compound Exercises\n"
                "Progressive Overload"
            )

        elif bmi >= 30:

            return (
                "Low Impact Cardio\n"
                "Walking\n"
                "Cycling\n"
                "Light Strength Training"
            )

        return (
            "30 min Mixed Workout\n"
            "Strength + Cardio\n"
            "Stretching"
        )

    # =====================================================
    # Diet Recommendation
    # =====================================================

    @staticmethod
    def diet_plan(goal):

        goal = str(goal).lower()

        if "lose" in goal:

            return (
                "High Protein\n"
                "Low Sugar\n"
                "Vegetables\n"
                "Healthy Fats"
            )

        elif "gain" in goal:

            return (
                "High Protein\n"
                "Complex Carbohydrates\n"
                "Healthy Calories"
            )

        return (
            "Balanced Diet\n"
            "Protein\n"
            "Whole Grains\n"
            "Fruits"
        )

    # =====================================================
    # Latest Recommendation
    # =====================================================

    @staticmethod
    def latest(user_id):
        """
        Return the latest recommendation for a user.
    """

        return (
            SavedRecommendation.query
            .filter_by(user_id=user_id)
            .order_by(SavedRecommendation.generated_at.desc())
            .first()
        )