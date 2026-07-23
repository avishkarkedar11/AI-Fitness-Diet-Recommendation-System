"""
Profile Service

Business logic for user fitness profiles.
"""

from app.extensions import db
from app.models.fitness_profile import FitnessProfile
from app.utils.enums import (
    Gender,
    FitnessGoal,
    ActivityLevel
)


class ProfileService:
    """
    Business logic for Fitness Profile.
    """

    @staticmethod
    def get_profile(user_id: int):
        """
        Return the user's fitness profile.
        """
        return FitnessProfile.query.filter_by(
            user_id=user_id
        ).first()

    @staticmethod
    def profile_exists(user_id: int) -> bool:
        """
        Check whether the user already has a profile.
        """
        return (
            ProfileService.get_profile(user_id)
            is not None
        )

    @staticmethod
    def create_profile(form, user_id: int):
        """
        Create a new fitness profile.
        """

        profile = FitnessProfile(

            # ==========================
            # User
            # ==========================

            user_id=user_id,

            # ==========================
            # Personal Details
            # ==========================

            age=form.age.data,
            gender=Gender(form.gender.data),

            # ==========================
            # Body Measurements
            # ==========================

            height_cm=form.height_cm.data,
            weight_kg=form.weight_kg.data,
            target_weight_kg=form.target_weight_kg.data,

            # ==========================
            # Fitness
            # ==========================

            goal=FitnessGoal(form.goal.data),
            activity_level=ActivityLevel(form.activity_level.data),

            # ==========================
            # Daily Activity
            # ==========================

            workout_hours=form.workout_hours.data,
            sleep_hours=form.sleep_hours.data,
            daily_steps=form.daily_steps.data,

            # ==========================
            # Dietary Preference
            # ==========================

            dietary_preference=form.dietary_preference.data,

            # ==========================
            # Health
            # ==========================

            water_intake_liters=form.water_intake_liters.data,
            medical_conditions=(
                form.medical_conditions.data
                if form.medical_conditions.data
                else "None"
            )
        )

        db.session.add(profile)
        db.session.commit()

        return profile

    @staticmethod
    def update_profile(profile, form):
        """
        Update an existing fitness profile.
        """

        # ==========================
        # Personal Details
        # ==========================

        profile.age = form.age.data
        profile.gender = Gender(form.gender.data)

        # ==========================
        # Body Measurements
        # ==========================

        profile.height_cm = form.height_cm.data
        profile.weight_kg = form.weight_kg.data
        profile.target_weight_kg = form.target_weight_kg.data

        # ==========================
        # Fitness
        # ==========================

        profile.goal = FitnessGoal(form.goal.data)
        profile.activity_level = ActivityLevel(
            form.activity_level.data
        )


        # ==========================
        # Daily Activity
        # ==========================

        profile.workout_hours = form.workout_hours.data
        profile.sleep_hours = form.sleep_hours.data
        profile.daily_steps = form.daily_steps.data

        # ==========================
        # Dietary Preference
        # ==========================

        profile.dietary_preference = (
            form.dietary_preference.data
        )

        # ==========================
        # Health
        # ==========================

        profile.water_intake_liters = (
            form.water_intake_liters.data
        )

        profile.medical_conditions = (
            form.medical_conditions.data
            if form.medical_conditions.data
            else "None"
        )

        db.session.commit()

        return profile