"""
Fitness Profile Model

Stores user fitness and health information.
"""

from datetime import datetime

from app.extensions import db
from app.utils.enums import (
    Gender,
    FitnessGoal,
    ActivityLevel,
)


class FitnessProfile(db.Model):
    """
    Fitness Profile Model
    """

    __tablename__ = "fitness_profiles"

    # ==========================
    # Primary Key
    # ==========================
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================
    # Foreign Key
    # ==========================
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    # ==========================
    # Personal Information
    # ==========================
    age = db.Column(
        db.Integer,
        nullable=False
    )

    gender = db.Column(
        db.Enum(Gender),
        nullable=False
    )

    height_cm = db.Column(
        db.Float,
        nullable=False
    )

    weight_kg = db.Column(
        db.Float,
        nullable=False
    )

    # ==========================
    # Fitness Targets
    # ==========================

    target_weight_kg = db.Column(
        db.Float,
        nullable=False
    )

    water_intake_liters = db.Column(
        db.Float,
        nullable=True
    )

    # ==========================
    # Fitness Goals
    # ==========================

    goal = db.Column(
        db.Enum(FitnessGoal),
        nullable=False
    )

    activity_level = db.Column(
        db.Enum(ActivityLevel),
        nullable=False
    )

    # ====================================
    # Daily Activity
    # ====================================

    workout_hours = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    sleep_hours = db.Column(
        db.Float,
        nullable=False,
        default=8.0
    )

    daily_steps = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # ====================================
    # Dietary Preference
    # ====================================

    dietary_preference = db.Column(
        db.String(50),
        nullable=False,
        default="Vegetarian"
    )

    # ==========================
    # Medical Information
    # ==========================

    medical_conditions = db.Column(
        db.Text,
        nullable=True,
        default="None"
    )

    # ==========================
    # Timestamps
    # ==========================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # ==========================
    # Relationships
    # ==========================

    user = db.relationship(
        "User",
        back_populates="fitness_profile"
    )

    # ==========================
    # String Representation
    # ==========================

    def __repr__(self):
        return (
            f"<FitnessProfile User ID: {self.user_id}>"
        )

    # ==========================
    # Calculated Properties
    # ==========================

    @property
    def bmi(self):
        """
        Calculate BMI dynamically.
        """

        if (
            self.height_cm is None
            or self.weight_kg is None
            or self.height_cm == 0
        ):
            return None

        height_m = self.height_cm / 100

        return round(
            self.weight_kg / (height_m ** 2),
            2
        )