"""
Recommendation Model
--------------------
This module defines the Recommendation SQLAlchemy model for storing AI/rule-based
advice generated for users. Each entry contains a daily health insight, its category
(e.g., nutrition, hydration, sleep, exercise, mood), a short actionable message,
and a more detailed explanation for why the recommendation was triggered.
"""

from datetime import datetime, timezone
from app import db


class Recommendation(db.Model):
    """
    Represents an automated wellness tip or health recommendation
    generated for a user based on their tracked habits and daily logs.
    """
    # Name of the database table
    __tablename__ = 'recommendations'

    # Primary key identifier
    id = db.Column(db.Integer, primary_key=True)

    # Reference to the user who received this recommendation
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # The calendar date this recommendation is relevant to
    recommendation_date = db.Column(db.Date, nullable=False)

    # Category of advice: 'sleep', 'water', 'exercise', 'nutrition', or 'mood'
    category = db.Column(db.String(50), nullable=False)

    # Short headline or call-to-action message displayed on the dashboard/advisor page
    message = db.Column(db.String(255), nullable=False)

    # Optional longer explanation detailing why this recommendation was given
    explanation = db.Column(db.Text)

    # Timestamp recorded when this recommendation was generated (stored in UTC)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship back to the User model (one-to-many: one user can have multiple recommendations)
    user = db.relationship('User', backref=db.backref('recommendations', lazy=True, cascade='all, delete-orphan'))
