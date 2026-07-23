"""
Profile Routes

Handles user fitness profile creation and updates.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
)

from app.forms.profile_form import ProfileForm
from app.services.profile_service import ProfileService

profile_bp = Blueprint(
    "profile",
    __name__
)


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    Create or Update User Profile
    """

    form = ProfileForm()

    profile = ProfileService.get_profile(current_user.id)

    # -----------------------------
    # POST Request
    # -----------------------------
    if form.validate_on_submit():

        if profile:

            ProfileService.update_profile(profile, form)

            flash(
                "Profile updated successfully.",
                "success"
            )

        else:

            ProfileService.create_profile(
                form,
                current_user.id
            )

            flash(
                "Profile created successfully.",
                "success"
            )

        return redirect(
            url_for("dashboard.dashboard")
        )

    # -----------------------------
    # GET Request
    # -----------------------------
    if profile:

        form.age.data = profile.age
        form.gender.data = profile.gender.name if hasattr(profile.gender, "name") else profile.gender
        form.height_cm.data = profile.height_cm
        form.weight_kg.data = profile.weight_kg
        form.target_weight_kg.data = profile.target_weight_kg
        form.goal.data = profile.goal.name if hasattr(profile.goal, "name") else profile.goal
        form.activity_level.data = profile.activity_level.name if hasattr(profile.activity_level, "name") else profile.activity_level
        form.workout_hours.data = profile.workout_hours
        form.sleep_hours.data = profile.sleep_hours
        form.daily_steps.data = profile.daily_steps
        form.dietary_preference.data = profile.dietary_preference
        form.water_intake_liters.data = profile.water_intake_liters
        form.medical_conditions.data = profile.medical_conditions

    return render_template(
        "dashboard/profile.html",
        form=form,
        profile=profile
    )