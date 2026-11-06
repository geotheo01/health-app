"""
Recommendation Data Access Object (DAO).
This file manages database interactions for AI-generated and rule-based health recommendations.
It provides methods to query recommendations by user and date, bulk save new recommendations,
and clear obsolete recommendations.
"""

from app.models.recommendation import Recommendation
from app import db


class RecommendationDAO:
    """
    DAO class handling CRUD operations for recommendation records in the database.
    """

    @staticmethod
    def get_by_user_and_date(user_id, date):
        """
        Retrieve all recommendations generated for a given user on a specific date.
        """
        # Query recommendations matching both the user ID and recommendation date
        return Recommendation.query.filter_by(user_id=user_id, recommendation_date=date).all()

    @staticmethod
    def count_total():
        """
        Count the total number of recommendations stored across all users.
        """
        # Return the total count of recommendation records for admin statistics
        return Recommendation.query.count()

    @staticmethod
    def get_all_for_user(user_id):
        """
        Fetch all recommendations for a user, ordered from most recent to oldest.
        """
        # Query by user ID and sort descending by creation timestamp
        return Recommendation.query.filter_by(user_id=user_id).order_by(Recommendation.created_at.desc()).all()

    @staticmethod
    def save(recommendation):
        """
        Save a single recommendation record into the database.
        """
        # Add the single recommendation to the session
        db.session.add(recommendation)
        # Commit the transaction to persist it
        db.session.commit()
        # Return the saved recommendation
        return recommendation

    @staticmethod
    def save_all(recommendations):
        """
        Bulk save a list of recommendation objects into the database in one transaction.
        """
        # Add all recommendation instances to the session at once
        db.session.add_all(recommendations)
        # Commit the transaction for all items
        db.session.commit()
        # Return the list of saved recommendations
        return recommendations

    @staticmethod
    def delete_for_user_and_date(user_id, date):
        """
        Remove all existing recommendations for a user on a given date
        (useful before regenerating fresh recommendations).
        """
        # Delete matching recommendation rows directly via query
        Recommendation.query.filter_by(user_id=user_id, recommendation_date=date).delete()
        # Commit the transaction to persist the deletion
        db.session.commit()

