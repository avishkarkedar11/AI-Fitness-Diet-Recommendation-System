"""
Progress Log Model

Stores user's fitness progress over time.
"""

from datetime import datetime

from app.extensions import db


class ProgressLog(db.Model):
    """
    Progress tracking model.
    """

    __tablename__ = "progress_logs"

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
    # Progress Data
    # ====================================

    weight_kg = db.Column(
        db.Float,
        nullable=False
    )

    body_fat_percentage = db.Column(
        db.Float,
        nullable=True
    )

    waist_cm = db.Column(
        db.Float,
        nullable=True
    )

    chest_cm = db.Column(
        db.Float,
        nullable=True
    )

    hip_cm = db.Column(
        db.Float,
        nullable=True
    )

    notes = db.Column(
        db.Text,
        nullable=True
    )

    # ====================================
    # Timestamp
    # ====================================

    recorded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ====================================
    # Relationship
    # ====================================

    user = db.relationship(
        "User",
        back_populates="progress_logs"
    )

    # ====================================
    # String Representation
    # ====================================

    def __repr__(self):
        return (
            f"<ProgressLog "
            f"User={self.user_id}, "
            f"Weight={self.weight_kg}kg>"
        )