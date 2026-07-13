"""
User Model

Stores user authentication and account information.
"""

from datetime import datetime

from flask_login import UserMixin

from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    """
    User Model
    """

    __tablename__ = "users"

    # ====================================
    # Primary Key
    # ====================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ====================================
    # Personal Information
    # ====================================

    first_name = db.Column(
        db.String(50),
        nullable=False
    )

    last_name = db.Column(
        db.String(50),
        nullable=False
    )

    username = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # ====================================
    # Account Status
    # ====================================

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True
    )

    # ====================================
    # Timestamps
    # ====================================

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

    # ====================================
    # Relationships
    # ====================================

    fitness_profile = db.relationship(
        "FitnessProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    progress_logs = db.relationship(
        "ProgressLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    saved_recommendations = db.relationship(
        "SavedRecommendation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    # ====================================
    # Helper Properties
    # ====================================

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    # ====================================
    # Password Methods
    # ====================================

    def set_password(self, password: str):
        """
        Hash and store the user's password.
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")


    def check_password(self, password: str) -> bool:
        """
        Verify the user's password.
        """
        return bcrypt.check_password_hash(self.password_hash, password)
    
    
    # ====================================
    # Representation
    # ====================================

    def __repr__(self):
        return f"<User {self.email}>"