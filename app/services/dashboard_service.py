"""
Dashboard Service

Collects all data required for the user dashboard.
"""

from app.services.profile_service import ProfileService
from app.services.progress_service import ProgressService
from app.services.progress_insight_service import ProgressInsightService
from app.services.bmi_service import BMIService
from app.services.calorie_service import CalorieService
from app.services.recommendation_service import RecommendationService


class DashboardService:
    """
    Dashboard business logic.
    """

    @staticmethod
    def get_dashboard_data(user_id):
        """
        Collect all dashboard data.
        """

        # =====================================
        # User Profile
        # =====================================

        profile = ProfileService.get_profile(user_id)

        if profile is None:
            return None

        # =====================================
        # Latest Progress
        # =====================================

        latest_progress = ProgressService.latest(user_id)

        current_weight = (
            latest_progress.weight_kg
            if latest_progress
            else profile.weight_kg
        )

        # =====================================
        # BMI
        # =====================================

        bmi = BMIService.calculate(
            current_weight,
            profile.height_cm
        )

        bmi_category = BMIService.category(bmi)

        # =====================================
        # Nutrition
        # =====================================

        nutrition = CalorieService.nutrition_report(
            profile
        )

        # =====================================
        # Progress Chart
        # =====================================

        chart = ProgressService.get_chart_data(
            user_id
        )

        # =====================================
        # Progress Insights
        # =====================================

        insights = ProgressInsightService.get_insights(
            user_id
        )

        # =====================================
        # Latest Recommendation
        # =====================================

        recommendation = RecommendationService.latest(
            user_id
        )

        # =====================================
        # Return Dashboard Data
        # =====================================

        return {

            "profile": profile,

            "current_weight": current_weight,

            "bmi": round(bmi, 2),

            "bmi_category": bmi_category,

            "nutrition": nutrition,

            "latest_progress": latest_progress,

            "chart": chart,

            "recommendation": recommendation,

            "insights": insights

        }