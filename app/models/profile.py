"""
Profile Model
-------------
This module defines the UserProfile database model for our Flask application.
It stores demographic and physical attributes for each user, such as age, gender,
height, weight, activity level, and health goals. This information is used
for calculating calorie needs, BMI, and personalized wellness tips.
"""

from datetime import datetime, timezone
from app import db


class UserProfile(db.Model):
    """
    Represents the physical profile and wellness attributes of a user.
    Maintains a 1-to-1 relationship with the User model.
    """
    # Name of the table in the database
    __tablename__ = 'user_profiles'

    # Primary key identifier for the profile record
    id = db.Column(db.Integer, primary_key=True)

    # Link back to the parent user record (unique=True enforces a 1-to-1 relationship)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # Demographic and body measurements
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)

    # Lifestyle attributes for fitness calculations
    activity_level = db.Column(db.String(50))  # e.g., 'sedentary', 'moderate', 'active'
    health_goal = db.Column(db.String(100))     # e.g., 'weight_loss', 'maintenance', 'muscle_gain'

    # Timestamps to track creation and latest modification in UTC
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship linking back to the User model (uselist=False    # One-to-one relationship bridging back to the User model
    user = db.relationship('User', backref=db.backref('profile', uselist=False, cascade='all, delete-orphan'))
