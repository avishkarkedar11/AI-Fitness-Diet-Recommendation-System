"""
Progress Routes

Handles user progress tracking.
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from app.forms.progress_form import ProgressForm

from app.services.progress_service import ProgressService
from app.services.progress_insight_service import ProgressInsightService


progress_bp = Blueprint(
    "progress",
    __name__
)


# =====================================================
# Progress Tracking
# =====================================================

@progress_bp.route(
    "/progress",
    methods=["GET", "POST"]
)
@login_required
def progress():
    """
    Display and manage user progress.
    """

    form = ProgressForm()

    # ==========================================
    # Save Progress
    # ==========================================

    if form.validate_on_submit():

        ProgressService.add_progress(
            form=form,
            user_id=current_user.id
        )

        flash(
            "Progress saved successfully!",
            "success"
        )

        return redirect(
            url_for("progress.progress")
        )

    # ==========================================
    # Load Progress History
    # ==========================================

    history = ProgressService.get_history(
        current_user.id
    )

    # ==========================================
    # Load Chart Data
    # ==========================================

    chart_data = ProgressService.get_chart_data(
        current_user.id
    )

    # ==========================================
    # Load Progress Insights
    # ==========================================

    insights = ProgressInsightService.get_insights(
        current_user.id
    )

    # ==========================================
    # Load Weight Forecast (LSTM Time Series)
    # ==========================================
    from app.ml.predictors.progress_predictor import ProgressPredictor
    forecast = []
    if chart_data and len(chart_data.get("weights", [])) >= 3:
        try:
            predictor = ProgressPredictor()
            forecast = predictor.forecast_weight(
                history_weights=chart_data["weights"],
                dates=chart_data["labels"],
                days_ahead=7
            )
        except Exception as e:
            print(f"Error generating progress forecast: {e}")

    # ==========================================
    # Render Template
    # ==========================================

    return render_template(
        "dashboard/progress.html",
        form=form,
        history=history,
        chart_data=chart_data,
        insights=insights,
        forecast=forecast
    )