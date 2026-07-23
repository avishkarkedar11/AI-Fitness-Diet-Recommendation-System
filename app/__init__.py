"""
app/__init__.py
----------------
Application Factory

Creates and configures the Flask application.
Initializes extensions and registers all blueprints.
"""

from flask import Flask

from app.config import Config
from app.extensions import (
    db,
    migrate,
    bcrypt,
    login_manager,
    oauth as oauth_ext,
)
from app.oauth import init_google_oauth
from app.models.user import User
from app.models.fitness_profile import FitnessProfile
from app.models.progress import ProgressLog
from app.models.recommendation import SavedRecommendation


def create_app():
    """
    Application Factory Function.
    Creates and returns a configured Flask application.
    """

    app = Flask(__name__)

    # ==============================
    # Load Configuration
    # ==============================
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    oauth_ext.init_app(app)
    init_google_oauth(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ==============================
    # Register Blueprints
    # ==============================
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.profile import profile_bp
    from app.routes.progress import progress_bp
    from app.routes.recommendation import recommendation_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # ==============================
    # Return Application
    # ==============================
    return app