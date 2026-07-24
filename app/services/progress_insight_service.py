"""
Progress Insight Service

Analyzes historical fitness progress and generates
professional insights for the Progress Tracking module.
"""

from app.models.progress import ProgressLog
from app.services.profile_service import ProfileService
from app.services.bmi_service import BMIService


class ProgressInsightService:
    """
    Generates progress insights using historical data.
    """

    # =====================================================
    # Main Function
    # =====================================================

    @staticmethod
    def get_insights(user_id):
        """
        Generate complete progress insights.
        """

        profile = ProfileService.get_profile(user_id)

        if profile is None:
            return None

        history = (
            ProgressLog.query
            .filter_by(user_id=user_id)
            .order_by(ProgressLog.recorded_at.asc())
            .all()
        )

        if len(history) == 0:
            return None

        first = history[0]
        latest = history[-1]

      
        weight = ProgressInsightService._weight_analysis(
            first,
            latest,
            profile
        )

        bmi = ProgressInsightService._bmi_analysis(
            first,
            latest,
            profile
        )

        body = ProgressInsightService._body_analysis(
            first,
            latest
        )

        goal = ProgressInsightService._goal_analysis(
            first,
            latest,
            profile
        )

        statistics = ProgressInsightService._statistics(
            history
        )

        summary = ProgressInsightService._generate_summary(
            weight,
            bmi,
            body,
            goal
        )

        return {

            "starting_weight": first.weight_kg,

            "current_weight": latest.weight_kg,

            "target_weight": profile.target_weight_kg,

            "weight": weight,

            "bmi": bmi,

            "body": body,

            "goal": goal,

            "statistics": statistics,

            "summary": summary

     }

    # =====================================================
    # Weight Analysis
    # =====================================================

    @staticmethod
    def _weight_analysis(first, latest, profile):
        """
        Analyze weight progress.
        """

        start_weight = first.weight_kg
        current_weight = latest.weight_kg

        change = round(
            current_weight - start_weight,
            2
        )

        if start_weight > 0:

            change_percent = round(
                (change / start_weight) * 100,
                2
            )

        else:

            change_percent = 0

        # -----------------------------
        # Trend
        # -----------------------------

        if change < 0:

            trend = "Lost"

            status = "Improved"

        elif change > 0:

            trend = "Gained"

            status = "Needs Attention"

        else:

            trend = "Stable"

            status = "Stable"

        return {

            "starting_weight": start_weight,

            "current_weight": current_weight,

            "weight_change": change,

            "weight_change_percent": abs(change_percent),

            "trend": trend,

            "status": status

        }

    # =====================================================
    # BMI Analysis
    # =====================================================

    @staticmethod
    def _bmi_analysis(first, latest, profile):
        """
        Analyze BMI progress.
        """

        starting_bmi = BMIService.calculate(
            first.weight_kg,
            profile.height_cm
        )

        current_bmi = BMIService.calculate(
            latest.weight_kg,
            profile.height_cm
        )

        difference = round(
            current_bmi - starting_bmi,
            2
        )

        return {

            "starting_bmi": starting_bmi,

            "current_bmi": current_bmi,

            "difference": difference,

            "category": BMIService.category(
                current_bmi
            )

        }
        # =====================================================
    # Body Composition Analysis
    # =====================================================

    @staticmethod
    def _body_analysis(first, latest):
        """
        Analyze body composition changes.
        """

        def calculate_change(start, current):
            if start is None or current is None:
                return None
            return round(current - start, 2)

        return {

            "waist": {

                "starting": first.waist_cm,

                "current": latest.waist_cm,

                "change": calculate_change(
                    first.waist_cm,
                    latest.waist_cm
                )

            }

        }

    # =====================================================
    # Goal Analysis
    # =====================================================

    @staticmethod
    def _goal_analysis(first, latest, profile):
        """
        Analyze goal progress.
        """

        goal_weight = profile.target_weight_kg
        current_weight = latest.weight_kg
        start_weight = first.weight_kg

        remaining = round(abs(current_weight - goal_weight), 2)

        # Determine if goal is weight loss vs weight gain
        is_weight_loss = (start_weight > goal_weight)
        if hasattr(profile, 'goal') and profile.goal:
            from app.utils.enums import FitnessGoal
            if profile.goal == FitnessGoal.LOSE_WEIGHT:
                is_weight_loss = True
            elif profile.goal == FitnessGoal.GAIN_WEIGHT:
                is_weight_loss = False

        if is_weight_loss:
            denominator = start_weight - goal_weight
            if denominator <= 0:
                progress = 100.0 if current_weight <= goal_weight else 0.0
            else:
                progress = ((start_weight - current_weight) / denominator) * 100.0
        else:
            denominator = goal_weight - start_weight
            if denominator <= 0:
                progress = 100.0 if current_weight >= goal_weight else 0.0
            else:
                progress = ((current_weight - start_weight) / denominator) * 100.0

        # Clamp result between 0 and 100
        progress = max(0.0, min(100.0, progress))
        progress = round(progress, 2)

        if progress >= 100:

            status = "Completed"

        elif progress >= 70:

            status = "On Track"

        elif progress >= 40:

            status = "Good Progress"

        else:

            status = "Needs Improvement"

        return {

            "target_weight": goal_weight,

            "starting_weight": start_weight,

            "current_weight": current_weight,

            "remaining_weight": remaining,

            "progress_percent": progress,

            "status": status

        }

    # =====================================================
    # Statistics
    # =====================================================

    @staticmethod
    def _statistics(history):
        """
        Return progress statistics.
        """

        first = history[0]
        latest = history[-1]

        tracking_days = (
            latest.recorded_at.date() -
            first.recorded_at.date()
        ).days

        return {

            "entries": len(history),

            "tracking_days": tracking_days,

            "first_record": first.recorded_at.strftime(
                "%d %b %Y"
            ),

            "last_record": latest.recorded_at.strftime(
                "%d %b %Y"
            )

        }

    # =====================================================
    # AI Coach Summary
    # =====================================================

    @staticmethod
    def _generate_summary(
        weight,
        bmi,
        body,
        goal
    ):
        """
        Generate professional progress summary.
        """

        summary = []

        if weight["weight_change"] < 0:

            summary.append(
                f"You have lost {abs(weight['weight_change'])} kg since your first entry."
            )

        elif weight["weight_change"] > 0:

            summary.append(
                f"You have gained {weight['weight_change']} kg since your first entry."
            )

        else:

            summary.append(
                "Your weight has remained stable."
            )

        if bmi["difference"] < 0:

            summary.append(
                "Your BMI has improved."
            )

        elif bmi["difference"] > 0:

            summary.append(
                "Your BMI has increased."
            )

        if (
            body["waist"]["change"] is not None and
            body["waist"]["change"] < 0
        ):

            summary.append(
                f"Waist reduced by {abs(body['waist']['change'])} cm."
            )

        if goal["status"] == "Completed":

            summary.append(
                "Congratulations! You have reached your target weight."
            )

        elif goal["status"] == "On Track":

            summary.append(
                "You are progressing well toward your target weight."
            )

        else:

            summary.append(
                "Stay consistent with your workout and nutrition plan."
            )

        return summary    