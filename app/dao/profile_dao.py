"""
Profile Data Access Object (DAO).
This file handles database operations related to user personal profiles,
including demographics, physical attributes (height, weight, age), and fitness metrics.
"""

from app.models.profile import UserProfile
from app import db


class ProfileDAO:
    """
    DAO class providing methods to query and persist UserProfile records.
    """

    @staticmethod
    def get_by_user_id(user_id):
        """
        Fetch the profile record for a specific user by user ID.
        """
        # Query the profiles table for the record linked to this user ID
        return UserProfile.query.filter_by(user_id=user_id).first()

    @staticmethod
    def save(profile):
        """
        Save or update a user profile in the database.
        """
        # Add the profile object to the database session
        db.session.add(profile)
        # Commit the transaction to save changes
        db.session.commit()
        # Return the persisted profile instance
        return profile

