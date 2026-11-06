"""
Favorite Meal Data Access Object (DAO).
This file handles all database queries and operations related to user favorite meals.
It separates direct database operations from the application business logic.
"""

from app import db
from app.models.favorite_meal import FavoriteMeal


class FavoriteMealDAO:
    """
    DAO class providing static helper methods to query, insert,
    update, and delete favorite meal records in the database.
    """

    @staticmethod
    def get_by_id(favorite_id):
        """
        Retrieve a single favorite meal by its primary key ID.
        """
        # Look up the favorite meal record using SQLAlchemy's session.get
        return db.session.get(FavoriteMeal, favorite_id)

    @staticmethod
    def get_user_favorites(user_id):
        """
        Get all favorite meals saved by a specific user, ordered alphabetically by title.
        """
        # Query favorites matching the user ID and order the results by title
        return FavoriteMeal.query.filter_by(user_id=user_id).order_by(FavoriteMeal.title).all()

    @staticmethod
    def save(favorite_meal):
        """
        Save a new or updated favorite meal record to the database.
        """
        # Stage the favorite meal object in the current database session
        db.session.add(favorite_meal)
        # Commit the transaction to persist the changes in the database
        db.session.commit()
        # Return the saved instance
        return favorite_meal

    @staticmethod
    def delete(favorite_meal):
        """
        Delete an existing favorite meal record from the database.
        """
        # Mark the favorite meal object for removal
        db.session.delete(favorite_meal)
        # Commit the transaction to remove it from the database
        db.session.commit()

