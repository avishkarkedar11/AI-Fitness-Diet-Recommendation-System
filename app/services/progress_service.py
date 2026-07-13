"""
Progress Service

Handles all business logic related to user progress tracking.
"""

from app.extensions import db
from app.models.progress import ProgressLog


class ProgressService:
    """
    Business logic for progress tracking.
    """

    @staticmethod
    def add_progress(form, user_id):
        """
        Create a new progress entry.
        """

        progress = ProgressLog(
            user_id=user_id,
            weight_kg=form.weight_kg.data,
            waist_cm=form.waist_cm.data,
            chest_cm=form.chest_cm.data,
            body_fat_percentage=form.body_fat_percentage.data,
            notes=form.notes.data
        )

        print("=" * 50)
        print("Creating Progress Entry...")
        print(f"User ID: {user_id}")
        print(f"Weight: {form.weight_kg.data}")
        print(f"Waist: {form.waist_cm.data}")
        print(f"Chest: {form.chest_cm.data}")
        print(f"Body Fat: {form.body_fat_percentage.data}")
        print(f"Notes: {form.notes.data}")

        try:
            db.session.add(progress)
            db.session.commit()

            print("✅ Progress inserted successfully!")
            print(f"Inserted ID: {progress.id}")
            print("=" * 50)

            return progress

        except Exception as e:
            db.session.rollback()

            print("=" * 50)
            print("❌ DATABASE ERROR")
            print(e)
            print("=" * 50)

            raise

    @staticmethod
    def get_history(user_id):
        """
        Return all progress records for a user.
        """

        return (
            ProgressLog.query
            .filter_by(user_id=user_id)
            .order_by(ProgressLog.recorded_at.desc())
            .all()
        )

    @staticmethod
    def latest(user_id):
        """
        Return the latest progress record.
        """

        return (
            ProgressLog.query
            .filter_by(user_id=user_id)
            .order_by(ProgressLog.recorded_at.desc())
            .first()
        )

    @staticmethod
    def get_chart_data(user_id):
        """
        Prepare progress data for Chart.js.
        """

        history = (
            ProgressLog.query
            .filter_by(user_id=user_id)
            .order_by(ProgressLog.recorded_at.asc())
            .all()
        )

        labels = []
        weights = []

        for item in history:
            labels.append(item.recorded_at.strftime("%d %b"))
            weights.append(item.weight_kg)

        return {
            "labels": labels,
            "weights": weights
        }

    @staticmethod
    def delete_progress(progress_id, user_id):
        """
        Delete a progress entry belonging to the user.
        """

        progress = ProgressLog.query.filter_by(
            id=progress_id,
            user_id=user_id
        ).first()

        if progress:
            db.session.delete(progress)
            db.session.commit()
            return True

        return False