"""
Goal Model
This module defines the Goal database model, which stores personal health
and fitness targets set by a user (such as calorie, water, sleep, and exercise goals).
"""

from datetime import datetime, timezone
from app import db


class Goal(db.Model):
    """
    Represents a user's active health and fitness goals.
    Maintains a 1-to-1 relationship with the User model, tracking daily
    targets for nutrition and lifestyle habits, as well as a target weight.
    """
    __tablename__ = 'goals'

    # Primary key for the goal record
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking directly to the user (unique=True enforces a 1-to-1 relationship)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # Daily target for caloric intake (in kcal)
    daily_calorie_goal = db.Column(db.Integer)

    # Daily hydration target in liters (e.g., 2.5 L)
    daily_water_goal = db.Column(db.Float)

    # Daily target for sleep duration in hours (e.g., 8.0 hrs)
    daily_sleep_goal = db.Column(db.Float)

    # Target minutes of physical exercise per week (e.g., 150 mins)
    weekly_exercise_goal = db.Column(db.Integer)

    # Desired or target body weight in kilograms
    target_weight = db.Column(db.Float)

    # Timestamps tracking when the goal was created and last updated in UTC
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Establishes a one-to-one relationship with the User model (a user has exactly one goal record)
    user = db.relationship('User', backref=db.backref('goal', uselist=False, cascade='all, delete-orphan'))
