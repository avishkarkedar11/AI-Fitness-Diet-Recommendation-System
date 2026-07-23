"""
Google OAuth Configuration
"""

from app.extensions import oauth


def init_google_oauth(app):
    """
    Register Google OAuth client.
    """

    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url=(
            "https://accounts.google.com/.well-known/openid-configuration"
        ),
        client_kwargs={
            "scope": "openid email profile"
        }
    )