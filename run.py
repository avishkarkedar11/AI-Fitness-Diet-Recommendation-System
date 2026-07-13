"""
run.py

Application entry point.
"""

from sqlalchemy import text

from app import create_app
from app.extensions import db

app = create_app()


@app.route("/db-test")
def db_test():
    """
    Test MySQL database connection.
    """
    try:
        db.session.execute(text("SELECT 1"))
        return "✅ Database Connected Successfully!"
    except Exception as e:
        return f"❌ Database Connection Failed!<br><br>{e}"


if __name__ == "__main__":
    app.run(debug=True)