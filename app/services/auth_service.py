"""
Authentication Service

Contains all business logic related to user authentication.
"""

from datetime import datetime

from sqlalchemy import or_

from app.extensions import db
from app.models.user import User


class AuthService:
    """
    Authentication Service
    """

    @staticmethod
    def username_exists(username: str) -> bool:
        """
        Check whether a username already exists.
        """
        return User.query.filter_by(username=username).first() is not None

    @staticmethod
    def email_exists(email: str) -> bool:
        """
        Check whether an email already exists.
        """
        return User.query.filter_by(email=email).first() is not None

    @staticmethod
    def register_user(form):
        """
        Register a new user.
        """

        if AuthService.username_exists(form.username.data):
            return False, "Username already exists."

        if AuthService.email_exists(form.email.data):
            return False, "Email already exists."

        user = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower()
        )

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return True, "Registration successful."

    @staticmethod
    def authenticate(username_or_email: str, password: str):
        """
        Authenticate using username or email.
        """

        user = User.query.filter(
            or_(
                User.username == username_or_email.strip(),
                User.email == username_or_email.lower()
            )
        ).first()

        if user is None:
            return None

        if not user.check_password(password):
            return None

        user.last_login = datetime.utcnow()
        db.session.commit()

        return user