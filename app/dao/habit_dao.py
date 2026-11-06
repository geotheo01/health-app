"""
Habit Data Access Object (DAO).
This file handles database queries and operations for tracking user lifestyle habits
such as daily activity level, dietary preferences, and sleep schedules.
"""

from app.models.user_habit import UserHabit
from app import db


class HabitDAO:
    """
    DAO class providing methods to fetch and persist user lifestyle habits in the database.
    """

    @staticmethod
    def get_by_user_id(user_id):
        """
        Find the habit record linked to a particular user by their user ID.
        """
        # Search for the first habit entry matching this user ID
        return UserHabit.query.filter_by(user_id=user_id).first()

    @staticmethod
    def save(habit):
        """
        Save or update a user's habit record in the database.
        """
        # Stage the habit model instance into the database session
        db.session.add(habit)
        # Commit the changes so they are written to the database
        db.session.commit()
        # Return the updated habit record
        return habit

