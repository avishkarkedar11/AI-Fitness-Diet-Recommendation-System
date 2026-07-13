"""
Application Enums

Contains all enums used throughout the application.
"""

from enum import Enum


class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class FitnessGoal(Enum):
    LOSE_WEIGHT = "Lose Weight"
    GAIN_WEIGHT = "Gain Weight"
    MAINTAIN_WEIGHT = "Maintain Weight"


class ActivityLevel(Enum):
    SEDENTARY = "Sedentary"
    LIGHTLY_ACTIVE = "Lightly Active"
    MODERATELY_ACTIVE = "Moderately Active"
    VERY_ACTIVE = "Very Active"
    EXTREMELY_ACTIVE = "Extremely Active"