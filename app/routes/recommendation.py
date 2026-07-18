"""
Recommendation Routes

Handles generation and viewing of AI recommendations.
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from app.services.recommendation_service import RecommendationService
from app.services.profile_service import ProfileService
from app.services.progress_service import ProgressService
from app.services.bmi_service import BMIService

recommendation_bp = Blueprint(
    "recommendation",
    __name__
)


# =====================================================
# Generate Recommendation
# =====================================================

@recommendation_bp.route("/recommendation/generate")
@login_required
def generate_recommendation():
    """
    Generate a new recommendation.
    """
    try:
        recommendation = RecommendationService.generate(
            current_user.id
        )

        if recommendation is None:

            flash(
                "Please complete your fitness profile first.",
                "warning"
            )

            return redirect(
                url_for("profile.profile")
            )

        flash(
            "Recommendation generated successfully!",
            "success"
        )

        return redirect(
            url_for("recommendation.view_recommendation")
        )
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("dashboard.dashboard"))


# =====================================================
# View Latest Recommendation
# =====================================================

@recommendation_bp.route("/recommendation")
@login_required
def view_recommendation():
    """
    Display the latest recommendation.
    """

    recommendation = RecommendationService.latest(
        current_user.id
    )

    if recommendation is None:

        flash(
            "No recommendation found. Generate one first.",
            "info"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    # ---------------------------------------
    # Get Profile
    # ---------------------------------------

    profile = ProfileService.get_profile(current_user.id)

    # ---------------------------------------
    # Latest Weight
    # ---------------------------------------

    latest_progress = ProgressService.latest(current_user.id)

    current_weight = (
        latest_progress.weight_kg
        if latest_progress
        else profile.weight_kg
    )

    # ---------------------------------------
    # Calculate BMI
    # ---------------------------------------

    bmi = BMIService.calculate(
        current_weight,
        profile.height_cm
    )

    bmi_category = BMIService.category(bmi)

    return render_template(
        "dashboard/recommendation.html",
        recommendation=recommendation,
        bmi=round(bmi, 2),
        bmi_category=bmi_category,
        current_weight=current_weight
    )


# =====================================================
# Regenerate Recommendation
# =====================================================

@recommendation_bp.route("/recommendation/regenerate")
@login_required
def regenerate_recommendation():
    """
    Generate a fresh recommendation.
    """
    try:
        RecommendationService.generate(
            current_user.id
        )
        flash(
            "Recommendation updated successfully!",
            "success"
        )
        return redirect(
            url_for("recommendation.view_recommendation")
        )
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("dashboard.dashboard"))