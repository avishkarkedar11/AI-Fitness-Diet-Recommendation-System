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

    # =====================================================
    # Generate Recommendation
    # =====================================================

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

        # ---------------------------------------------
        # BMI
        # ---------------------------------------------

        bmi = BMIService.calculate(
            current_weight,
            profile.height_cm
        )

        # ---------------------------------------------
        # Nutrition Report
        # ---------------------------------------------

        nutrition = CalorieService.nutrition_report(
            profile
        )
        
        

        # ---------------------------------------------
        # Workout Recommendation
        # ---------------------------------------------

        workout = RecommendationService.workout_plan(
            profile,
            bmi
        )

        # ---------------------------------------------
        # Diet Recommendation
        # ---------------------------------------------

        diet = RecommendationService.diet_plan(
            profile,
            nutrition
        )

        # ---------------------------------------------
        # Save Recommendation
        # ---------------------------------------------

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
    def workout_plan(profile, bmi):
        """
        Generate personalized workout plan.
        """

        workout = []

        goal = profile.goal.value.lower()

        # ---------------------------------------------
        # Goal Based Workout
        # ---------------------------------------------

        if "lose" in goal:

            workout.extend([
                "45 min Cardio",
                "30 min Strength Training",
                "10,000 Daily Steps"
            ])

        elif "gain" in goal:

            workout.extend([
                "60 min Weight Training",
                "Compound Exercises",
                "Progressive Overload"
            ])

        else:

            workout.extend([
                "30 min Mixed Workout",
                "Strength + Cardio",
                "Flexibility Training"
            ])

        # ---------------------------------------------
        # BMI Recommendation
        # ---------------------------------------------

        if bmi >= 30:

            workout.append(
                "Prefer Low Impact Exercises (Walking/Cycling)"
            )

        elif bmi < 18.5:

            workout.append(
                "Focus on Muscle Building Exercises"
            )

        # ---------------------------------------------
        # Workout Hours
        # ---------------------------------------------

        if profile.workout_hours < 1:

            workout.append(
                "Increase workout duration gradually."
            )

        elif profile.workout_hours > 2:

            workout.append(
                "Ensure adequate recovery between sessions."
            )

        # ---------------------------------------------
        # Daily Steps
        # ---------------------------------------------

        if profile.daily_steps < 5000:

            workout.append(
                "Increase daily walking activity."
            )

        elif profile.daily_steps >= 10000:

            workout.append(
                "Excellent daily activity level."
            )

        # ---------------------------------------------
        # Sleep
        # ---------------------------------------------

        if profile.sleep_hours < 7:

            workout.append(
                "Improve sleep to support muscle recovery."
            )

        # ---------------------------------------------
        # Medical Conditions
        # ---------------------------------------------

        if (
            profile.medical_conditions
            and profile.medical_conditions.lower() != "none"
        ):

            workout.append(
                f"Exercise with caution due to: {profile.medical_conditions}."
            )

        return workout
    
        # =====================================================
    # Diet Recommendation
    # =====================================================

    @staticmethod
    def diet_plan(profile, nutrition):
        """
        Generate personalized diet plan.
        """

        diet = []

        goal = profile.goal.value.lower()

        # ---------------------------------------------
        # Goal Based Diet
        # ---------------------------------------------

        if "lose" in goal:

            diet.extend([
                "High Protein Meals",
                "Low Sugar Intake",
                "High Fiber Vegetables",
                "Healthy Fats"
            ])

        elif "gain" in goal:

            diet.extend([
                "High Protein Meals",
                "Complex Carbohydrates",
                "Calorie Surplus Diet",
                "Healthy Snacks"
            ])

        else:

            diet.extend([
                "Balanced Diet",
                "Whole Grains",
                "Lean Protein",
                "Fresh Fruits & Vegetables"
            ])

        # ---------------------------------------------
        # Dietary Preference
        # ---------------------------------------------

        preference = profile.dietary_preference.lower()

        if preference == "vegetarian":

            diet.append(
                "Protein Sources: Paneer, Milk, Soybean, Lentils"
            )

        elif preference == "non-vegetarian":

            diet.append(
                "Protein Sources: Chicken, Eggs, Fish"
            )

        elif preference == "vegan":

            diet.append(
                "Protein Sources: Tofu, Soy Milk, Chickpeas"
            )

        elif preference == "eggetarian":

            diet.append(
                "Protein Sources: Eggs, Paneer, Lentils"
            )

        elif preference == "jain":

            diet.append(
                "Follow Jain dietary guidelines with high-protein alternatives."
            )

        # ---------------------------------------------
        # Water Intake
        # ---------------------------------------------

        diet.append(
            f"Drink at least {nutrition['water_liters']} L water daily."
        )

        # ---------------------------------------------
        # Calories
        # ---------------------------------------------

        diet.append(
            f"Daily Calories: {nutrition['target_calories']} kcal"
        )

        # ---------------------------------------------
        # Macronutrients
        # ---------------------------------------------

        diet.append(
            f"Protein: {nutrition['protein_g']} g/day"
        )

        diet.append(
            f"Carbohydrates: {nutrition['carbs_g']} g/day"
        )

        diet.append(
            f"Healthy Fats: {nutrition['fat_g']} g/day"
        )

        # ---------------------------------------------
        # Medical Conditions
        # ---------------------------------------------

        if (
            profile.medical_conditions
            and profile.medical_conditions.lower() != "none"
        ):

            diet.append(
                f"Consult your healthcare provider regarding your diet because of: {profile.medical_conditions}."
            )

        return diet

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
            .order_by(
                SavedRecommendation.generated_at.desc()
            )
            .first()
        )