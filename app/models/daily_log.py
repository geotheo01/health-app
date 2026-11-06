"""
Daily Log Model
This module defines the DailyLog database model used for tracking daily health metrics,
including sleep, water intake, exercise time, mood ratings, and body weight.
"""

from datetime import datetime, timezone
from app import db


class DailyLog(db.Model):
    """
    Stores a daily health check-in record for a user on a given date.
    Tracks quantitative metrics (sleep hours, water intake, exercise minutes, weight)
    along with qualitative feedback (mood score and personal notes).
    A user can have at most one log entry per calendar day.
    """
    __tablename__ = 'daily_logs'

    # Primary key for the daily log entry
    id = db.Column(db.Integer, primary_key=True)

    # Reference to the user who submitted this daily log
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Calendar date that this log corresponds to (YYYY-MM-DD)
    log_date = db.Column(db.Date, nullable=False)

    # Total hours of sleep recorded for the day
    sleep_hours = db.Column(db.Float)

    # Total volume of water consumed throughout the day in liters
    water_liters = db.Column(db.Float)

    # Total duration of physical exercise or workout in minutes
    exercise_minutes = db.Column(db.Integer)

    # Subjective rating of mood or wellbeing (e.g., scale from 1 to 5)
    mood_score = db.Column(db.Integer)

    # Body weight measurement in kilograms
    weight_kg = db.Column(db.Float)

    # Optional journal entry or personal reflections for the day
    notes = db.Column(db.Text)

    # Timestamps tracking record creation and last modification in UTC
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Unique constraint ensuring a user cannot submit duplicate logs for the same date
    __table_args__ = (db.UniqueConstraint('user_id', 'log_date', name='_user_date_uc'),)

    # Relationship linking back to User model    # Relationship to the user, allowing access like user.logs
    user = db.relationship('User', backref=db.backref('logs', lazy=True, cascade='all, delete-orphan'))
