"""
Progress Form

Collects user fitness progress.
"""

from flask_wtf import FlaskForm
from wtforms import (
    FloatField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    Optional
)


class ProgressForm(FlaskForm):
    """
    User Progress Form
    """

    weight_kg = FloatField(
        "Current Weight (kg)",
        validators=[
            DataRequired(),
            NumberRange(min=20, max=300)
        ]
    )

    waist_cm = FloatField(
        "Waist (cm)",
        validators=[
            Optional(),
            NumberRange(min=20, max=250)
        ],
        filters=[lambda x: x if x is not None and str(x).strip() != "" else None]
    )

    notes = TextAreaField(
        "Notes",
        validators=[Optional()]
    )

    submit = SubmitField(
        "Save Progress"
    )