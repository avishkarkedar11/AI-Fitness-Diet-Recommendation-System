"""
Models Package

Imports all database models so that Flask-Migrate
can detect them during migrations.
"""

from app.models.user import User
from app.models.user import User
from app.models.fitness_profile import FitnessProfile

# Future imports
# from app.models.fitness_profile import FitnessProfile
# from app.models.workout import Workout
# from app.models.diet import Diet
# from app.models.recommendation import Recommendation
# from app.models.progress import Progress