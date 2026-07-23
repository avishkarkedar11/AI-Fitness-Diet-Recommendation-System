"""
Profile Form

Collects user fitness profile information.
"""

from flask_wtf import FlaskForm

from wtforms import (
    IntegerField,
    FloatField,
    SelectField,
    SubmitField,
    TextAreaField
)

from wtforms.validators import (
    DataRequired,
    NumberRange,
    Optional
)


class ProfileForm(FlaskForm):
    """
    User Fitness Profile Form
    """

    # =====================================
    # Personal Information
    # =====================================

    age = IntegerField(
        "Age",
        validators=[
            DataRequired(),
            NumberRange(min=10, max=100)
        ]
    )

    gender = SelectField(
        "Gender",
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other")
        ],
        validators=[DataRequired()]
    )

    # =====================================
    # Body Measurements
    # =====================================

    height_cm = FloatField(
        "Height (cm)",
        validators=[
            DataRequired(),
            NumberRange(min=100, max=250)
        ]
    )

    weight_kg = FloatField(
        "Weight (kg)",
        validators=[
            DataRequired(),
            NumberRange(min=20, max=300)
        ]
    )
    
    # =====================================
    # Fitness Targets
    # =====================================

    target_weight_kg = FloatField(
        "Target Weight (kg)",
        validators=[
            DataRequired(),
            NumberRange(min=20, max=300)
        ]
    )

    water_intake_liters = FloatField(
    "Water Intake (Liters)",
    validators=[
        Optional(),
        NumberRange(min=0.5, max=10)
    ]
)
    # =====================================
    # Daily Activity (Required by Project)
    # =====================================

    workout_hours = FloatField(
        "Workout Hours / Day",
        validators=[
            DataRequired(),
            NumberRange(min=0, max=12)
        ]
    )

    sleep_hours = FloatField(
        "Sleep Hours / Day",
        validators=[
            DataRequired(),
            NumberRange(min=1, max=24)
        ]
    )

    daily_steps = IntegerField(
        "Daily Steps",
        validators=[
            DataRequired(),
            NumberRange(min=0, max=100000)
        ]
    )

    # =====================================
    # Activity Level
    # =====================================

    activity_level = SelectField(
    "Activity Level",
    choices=[
        ("Sedentary", "Sedentary"),
        ("Lightly Active", "Lightly Active"),
        ("Moderately Active", "Moderately Active"),
        ("Very Active", "Very Active"),
        ("Extremely Active", "Extremely Active")
    ],
    validators=[DataRequired()]
)

    # =====================================
    # Fitness Goal
    # =====================================

    goal = SelectField(
    "Fitness Goal",
    choices=[
        ("Lose Weight", "Lose Weight"),
        ("Gain Weight", "Gain Weight"),
        ("Maintain Weight", "Maintain Weight")
    ],
    validators=[DataRequired()]
)

    # =====================================
    # Dietary Preference
    # =====================================

    dietary_preference = SelectField(
        "Dietary Preference",
        choices=[
            ("Vegetarian", "Vegetarian"),
            ("Non-Vegetarian", "Non-Vegetarian"),
            ("Vegan", "Vegan"),
            ("Eggetarian", "Eggetarian"),
            ("Jain", "Jain")
        ],
        validators=[DataRequired()]
    )

    # =====================================
    # Medical Conditions
    # =====================================

    medical_conditions = TextAreaField(
        "Medical Conditions",
        validators=[Optional()]
    )

    # =====================================
    # Submit
    # =====================================

    submit = SubmitField(
        "Save Profile"
    )