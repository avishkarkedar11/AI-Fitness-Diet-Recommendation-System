"""
Saved Recommendation Model

Stores AI-generated workout and diet recommendations.
"""

from datetime import datetime

from app.extensions import db


class SavedRecommendation(db.Model):
    """
    Stores saved AI recommendations.
    """

    __tablename__ = "saved_recommendations"

    # ====================================
    # Primary Key
    # ====================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ====================================
    # Foreign Key
    # ====================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # ====================================
    # AI Recommendation
    # ====================================

    workout_plan = db.Column(
        db.JSON,
        nullable=False
    )

    diet_plan = db.Column(
        db.JSON,
        nullable=False
    )

    # ====================================
    # Nutrition Targets
    # ====================================

    daily_calories = db.Column(
        db.Integer,
        nullable=False
    )

    protein_g = db.Column(
        db.Float,
        nullable=False
    )

    carbs_g = db.Column(
        db.Float,
        nullable=False
    )

    fats_g = db.Column(
        db.Float,
        nullable=False
    )

    # ====================================
    # Timestamp
    # ====================================

    generated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ====================================
    # Relationship
    # ====================================

    user = db.relationship(
        "User",
        back_populates="saved_recommendations"
    )

    # ====================================
    # Representation
    # ====================================

    def __repr__(self):
        return (
            f"<SavedRecommendation "
            f"User={self.user_id}, "
            f"Date={self.generated_at}>"
        )