"""
Login Form

Handles user authentication.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Length
)


class LoginForm(FlaskForm):
    """
    User Login Form
    """

    username_or_email = StringField(
        "Username or Email",
        validators=[
            DataRequired(message="Username or Email is required."),
            Length(min=3, max=120)
        ],
        render_kw={
            "placeholder": "Enter your username or email"
        }
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(min=8)
        ],
        render_kw={
            "placeholder": "Enter your password"
        }
    )

    remember_me = BooleanField(
        "Remember Me"
    )

    submit = SubmitField(
        "Login"
    )