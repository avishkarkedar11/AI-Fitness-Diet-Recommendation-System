"""
Authentication Service

Contains all business logic related to user authentication.
"""

import re
from datetime import datetime

from sqlalchemy import or_

from app.extensions import db
from app.models.user import User


class AuthService:
    """
    Authentication Service
    """

    # ==================================================
    # Existing Helper Methods
    # ==================================================

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

    # ==================================================
    # Existing Registration
    # ==================================================

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
            email=form.email.data.strip().lower(),
            auth_provider="local"
        )

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return True, "Registration successful."

    # ==================================================
    # Existing Login
    # ==================================================

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

    # ==================================================
    # Google Authentication
    # ==================================================

    @staticmethod
    def get_user_by_email(email: str):
        """
        Return user by email.
        """
        return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def generate_username(email: str) -> str:
        """
        Generate a unique username from email.
        """

        base_username = email.split("@")[0]
        base_username = re.sub(r"[^a-zA-Z0-9_]", "", base_username)

        if not base_username:
            base_username = "user"

        username = base_username
        counter = 1

        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1

        return username

    @staticmethod
    def authenticate_google_user(user_info):
        """
        Authenticate or create a Google user.
        """

        email = user_info["email"].lower()

        # Existing user
        user = AuthService.get_user_by_email(email)

        if user:
            user.last_login = datetime.utcnow()

            # If this was an old local account,
            # allow Google login as well.
            user.auth_provider = "google"

            db.session.commit()
            return user

        # Create new Google user
        first_name = user_info.get("given_name", "").strip()
        last_name = user_info.get("family_name", "").strip()

        if not first_name:
            first_name = "User"

        if not last_name:
            last_name = "-"

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=AuthService.generate_username(email),
            email=email,
            auth_provider="google",
            password_hash=None,
            last_login=datetime.utcnow()
        )

        db.session.add(user)
        db.session.commit()

        return user