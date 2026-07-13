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
        form.gender.data = profile.gender.name
        form.height_cm.data = profile.height_cm
        form.weight_kg.data = profile.weight_kg
        form.target_weight_kg.data = profile.target_weight_kg
        form.goal.data = profile.goal.name
        form.activity_level.data = profile.activity_level.name
        form.body_fat_percentage.data = profile.body_fat_percentage
        form.water_intake_liters.data = profile.water_intake_liters
        form.medical_conditions.data = profile.medical_conditions

    return render_template(
        "dashboard/profile.html",
        form=form,
        profile=profile
    )