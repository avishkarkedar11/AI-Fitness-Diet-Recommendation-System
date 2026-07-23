"""
Authentication Routes

Handles Google authentication and logout.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    url_for
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from authlib.integrations.flask_client import OAuthError

from app.extensions import oauth
from app.services.auth_service import AuthService


auth_bp = Blueprint(
    "auth",
    __name__
)


# ==================================================
# Google Login
# ==================================================

@auth_bp.route("/login")
def login():
    """
    Redirect user to Google Sign-In.
    """

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    redirect_uri = url_for(
        "auth.google_authorized",
        _external=True
    )

    return oauth.google.authorize_redirect(redirect_uri)


# ==================================================
# Google Callback
# ==================================================

@auth_bp.route("/login/google/authorized")
def google_authorized():
    """
    Google OAuth callback.
    """

    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get("userinfo")

        if user_info is None:
            user_info = oauth.google.userinfo()

    except OAuthError:
        flash(
            "Google authentication failed.",
            "danger"
        )
        return redirect(url_for("auth.login"))

    user = AuthService.authenticate_google_user(user_info)

    login_user(user)

    flash(
        f"Welcome, {user.first_name}!",
        "success"
    )

    return redirect(url_for("dashboard.home"))


# ==================================================
# Logout
# ==================================================

@auth_bp.route("/logout")
@login_required
def logout():
    """
    Logout current user.
    """

    logout_user()

    flash(
        "You have been logged out successfully.",
        "info"
    )

    return redirect(url_for("auth.login"))