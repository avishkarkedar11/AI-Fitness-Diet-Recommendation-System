"""
Flask Extensions

Initializes all Flask extensions.
"""
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

# Database
db = SQLAlchemy()

# Migration
migrate = Migrate()

# Password Hashing
bcrypt = Bcrypt()

# Authentication
login_manager = LoginManager()

# oAuth
oauth = OAuth()

 
# Login Configuration
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"