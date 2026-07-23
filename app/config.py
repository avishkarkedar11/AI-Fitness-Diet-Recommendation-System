"""
app/config.py
--------------
Application configuration settings.

This module loads environment variables and provides
configuration values for the Flask application.
"""

import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env (if present)
load_dotenv()


class Config:
    """Base configuration class."""

    # ==========================
    # Flask Configuration
    # ==========================
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "this_is_a_development_secret_key_change_in_production"
    )

    # ==========================
    # MySQL Database Configuration
    # ==========================
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "ai_fitness_db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))

    SQLALCHEMY_DATABASE_URI = (
      f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
      f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
   )

    # ==========================
    # SQLAlchemy Settings
    # ==========================
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {
            "ssl": {}
        } if os.getenv("DB_HOST", "").endswith(".aivencloud.com") else {}
    }
    
    # ==========================
    # Google OAuth Configuration
    # ==========================
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # ==========================
    # Upload Settings
    # ==========================
    UPLOAD_FOLDER = "app/static/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ==========================
    # Session Settings
    # ==========================
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Enable this only when using HTTPS in production
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"