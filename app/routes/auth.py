"""
Authentication Routes

Handles user registration, login and logout.
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

from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm
from app.services.auth_service import AuthService

auth_bp = Blueprint(
    "auth",
    __name__
)


# ==================================================
# Register
# ==================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    User Registration
    """

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    form = RegisterForm()

    if form.validate_on_submit():

        success, message = AuthService.register_user(form)

        if success:
            flash(message, "success")
            return redirect(url_for("auth.login"))

        flash(message, "danger")

    return render_template(
        "auth/register.html",
        form=form
    )


# ==================================================
# Login
# ==================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    User Login
    """

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    form = LoginForm()

    if form.validate_on_submit():

        user = AuthService.authenticate(
            form.username_or_email.data,
            form.password.data
        )

        if user:

            login_user(
                user,
                remember=form.remember_me.data
            )

            flash(
                f"Welcome back, {user.first_name}!",
                "success"
            )

            return redirect(
                url_for("dashboard.home")
            )

        flash(
            "Invalid username/email or password.",
            "danger"
        )

    return render_template(
        "auth/login.html",
        form=form
    )


# ==================================================
# Logout
# ==================================================

@auth_bp.route("/logout")
@login_required
def logout():
    """
    User Logout
    """

    logout_user()

    flash(
        "You have been logged out successfully.",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )