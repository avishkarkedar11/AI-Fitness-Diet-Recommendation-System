from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    current_user
)

from app.services.dashboard_service import DashboardService

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route("/")
def home():
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    data = DashboardService.get_dashboard_data(current_user.id)

    if data is None:
        return redirect(url_for("profile.profile"))

    return render_template(
        "dashboard/dashboard.html",
        data=data
    )