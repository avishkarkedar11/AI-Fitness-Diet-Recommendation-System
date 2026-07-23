"""
Authentication Routes

Handles Google authentication and logout.
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
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
from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm
from app.services.auth_service import AuthService


auth_bp = Blueprint(
    "auth",
    __name__
)


# ==================================================
# Login Page (Form & Credentials)
# ==================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Render login page and handle credentials login.
    """

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = AuthService.authenticate(
            username_or_email=form.username_or_email.data,
            password=form.password.data
        )

        if user:
            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.first_name}!", "success")
            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid username/email or password.", "danger")

    return render_template("auth/login.html", form=form)


# ==================================================
# Registration Page
# ==================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Render registration page and handle user registration.
    """

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = RegisterForm()

    if form.validate_on_submit():
        success, message = AuthService.register_user(form)

        if success:
            flash("Registration successful! Please sign in.", "success")
            return redirect(url_for("auth.login"))

        flash(message, "danger")

    return render_template("auth/register.html", form=form)


# ==================================================
# Google Login
# ==================================================

@auth_bp.route("/login/google")
def google_login():
    """
    Redirect user to Google Sign-In.
    """

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

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

    return redirect(url_for("dashboard.dashboard"))


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