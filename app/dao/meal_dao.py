"""
Meal Data Access Object (DAO).
This file contains database operations for logged meals and nutritional records.
It encapsulates queries for fetching meals by user, date ranges, counts, and handles
saving and deleting meal entities via SQLAlchemy.
"""

from app.models.meal import Meal, MealItem
from app import db


class MealDAO:
    """
    DAO class handling database queries and persistence logic for the Meal model.
    """

    @staticmethod
    def get_user_meals(user_id):
        """
        Retrieve all meals logged by a specific user, sorted newest first
        by meal date and creation timestamp.
        """
        # Query meals for this user and order descending by meal date and created timestamp
        return Meal.query.filter_by(user_id=user_id).order_by(Meal.meal_date.desc(), Meal.created_at.desc()).all()

    @staticmethod
    def get_user_meals_in_range(user_id, start_date, end_date):
        """
        Fetch all meals for a user logged within an inclusive date range
        (used for weekly charts, history views, and summary reports).
        """
        # Filter meals by user ID and date boundary, ordered newest to oldest
        return Meal.query.filter(
            Meal.user_id == user_id,
            Meal.meal_date >= start_date,
            Meal.meal_date <= end_date
        ).order_by(Meal.meal_date.desc()).all()

    @staticmethod
    def get_by_id(meal_id):
        """
        Find and return a single meal entry by its primary key ID.
        """
        # Cast meal_id to integer and retrieve via SQLAlchemy session.get
        return db.session.get(Meal, int(meal_id))

    @staticmethod
    def count_total():
        """
        Count the total number of meal records across all users in the system.
        """
        # Execute a COUNT query on the meals table for admin statistics
        return Meal.query.count()

    @staticmethod
    def get_user_meals_by_date(user_id, meal_date):
        """
        Get all meals logged by a specific user on a specific calendar date.
        """
        # Filter meals matching both the user ID and the target date
        return Meal.query.filter_by(user_id=user_id, meal_date=meal_date).all()

    @staticmethod
    def save(meal):
        """
        Save a new meal or update an existing meal record in the database.
        """
        # Stage the meal entity in the current session
        db.session.add(meal)
        # Commit the transaction to persist changes
        db.session.commit()
        # Return the saved meal instance
        return meal

    @staticmethod
    def delete(meal):
        """
        Delete a meal record from the database (associated meal items will cascade delete).
        """
        # Mark the meal record for deletion
        db.session.delete(meal)
        # Commit the transaction to apply deletion
        db.session.commit()

