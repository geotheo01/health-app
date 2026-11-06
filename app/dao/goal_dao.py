"""
Goal Data Access Object (DAO).
This file manages database operations for user wellness and nutrition goals.
It handles fetching a user's goal record as well as saving/updating goals in the database.
"""

from app.models.goal import Goal
from app import db


class GoalDAO:
    """
    DAO class responsible for accessing and persisting user health goal records.
    """

    @staticmethod
    def get_by_user_id(user_id):
        """
        Retrieve the health and fitness goal for a given user.
        """
        # Query the goals table and get the first matching record for this user
        return Goal.query.filter_by(user_id=user_id).first()

    @staticmethod
    def save(goal):
        """
        Save or update a Goal record in the database.
        """
        # Add the goal instance to the database session
        db.session.add(goal)
        # Commit the transaction to save changes to the database
        db.session.commit()
        # Return the persisted goal object
        return goal

