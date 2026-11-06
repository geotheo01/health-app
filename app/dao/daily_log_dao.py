"""
Data Access Object (DAO) for Daily Log domain operations.

This module acts as the Data Access Object within the Model-View-Controller (MVC) architecture
for the application. It centralizes all database queries related to the `DailyLog` model, 
abstracting SQL interactions away from controller routes and enforcing separation of concerns.
"""

from app.models.daily_log import DailyLog
from app import db

class DailyLogDAO:
    """
    DAO class handling persistence operations for DailyLog instances.
    Provides static helper methods to perform CRUD operations via SQLAlchemy.
    """

    @staticmethod
    def get_user_logs(user_id):
        """
        Fetch all daily logs belonging to a specific user, sorted by date.

        Args:
            user_id (int): The unique identifier of the target user.

        Returns:
            list[DailyLog]: A list of daily log objects sorted in descending date order.
        """
        # Query logs filtered by user ID and order chronologically (newest entries first)
        return DailyLog.query.filter_by(user_id=user_id).order_by(DailyLog.log_date.desc()).all()

    @staticmethod
    def get_user_logs_in_range(user_id, start_date, end_date):
        """
        Retrieve user logs recorded within a designated date window.

        Args:
            user_id (int): The unique identifier of the user.
            start_date (date/str): Lower bound of the date range filter.
            end_date (date/str): Upper bound of the date range filter.

        Returns:
            list[DailyLog]: Matching daily log records sorted descending by date.
        """
        # Apply composite filtering for user ownership and inclusive date boundaries
        return DailyLog.query.filter(
            DailyLog.user_id == user_id,
            DailyLog.log_date >= start_date,
            DailyLog.log_date <= end_date
        ).order_by(DailyLog.log_date.desc()).all()

    @staticmethod
    def get_by_id(log_id):
        """
        Find a specific daily log by its primary key ID.

        Args:
            log_id (int | str): Primary key identifier of the log record.

        Returns:
            DailyLog | None: The matching DailyLog object, or None if not found.
        """
        # Explicitly cast to integer to prevent type errors during lookup
        return db.session.get(DailyLog, int(log_id))

    @staticmethod
    def count_total():
        """
        Count the total number of daily log entries across all users in the system.

        Returns:
            int: Aggregate count of daily logs.
        """
        # Execute aggregate query across the table
        return DailyLog.query.count()

    @staticmethod
    def get_by_user_and_date(user_id, log_date):
        """
        Find a unique daily log entry for a specific user on a given date.
        Useful for preventing duplicate entries per user per day.

        Args:
            user_id (int): The unique identifier of the user.
            log_date (date/str): The date to check for an existing entry.

        Returns:
            DailyLog | None: The record if present, otherwise None.
        """
        # Search for exact user and date combination
        return DailyLog.query.filter_by(user_id=user_id, log_date=log_date).first()

    @staticmethod
    def save(log):
        """
        Persist a new or modified DailyLog instance into the database session.

        Args:
            log (DailyLog): The model instance to save.

        Returns:
            DailyLog: The persisted log instance with updated session state.
        """
        # Stage object addition and commit the active transaction
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def delete(log):
        """
        Remove a DailyLog instance permanently from the database.

        Args:
            log (DailyLog): The model instance to be deleted.
        """
        # Flag record for removal and write changes to database
        db.session.delete(log)
        db.session.commit()
