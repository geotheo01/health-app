"""
daily_log_service.py
Service layer for managing user daily health logs.
Provides business validation and CRUD actions for logging sleep, water intake,
exercise duration, mood ratings, body weight, and personal notes for any date,
as well as a shortcut method for quick water intake logging.
"""

from app.dao.daily_log_dao import DailyLogDAO
from app.models.daily_log import DailyLog
from datetime import datetime


class DailyLogService:
    """
    Service class handling operations and business validation for daily logs.
    """

    @staticmethod
    def validate_log_data(data):
        """
        Validates the values submitted in a daily log form to ensure they fall
        within reasonable, realistic physical bounds.
        
        Parameters:
            data (dict): Dictionary containing raw or converted input values.
            
        Returns:
            tuple: (bool is_valid, str | None error_message)
        """
        sleep = data.get('sleep_hours')
        water = data.get('water_liters')
        exercise = data.get('exercise_minutes')
        mood = data.get('mood_score')

        # Sleep cannot be negative or exceed hours in a day
        if sleep is not None and (sleep < 0 or sleep > 24):
            return False, "Sleep hours must be between 0 and 24."
        # Water volume cannot be negative
        if water is not None and water < 0:
            return False, "Water liters cannot be negative."
        # Exercise duration cannot be negative
        if exercise is not None and exercise < 0:
            return False, "Exercise minutes cannot be negative."
        # Mood score is defined on a standard 1-to-10 Likert scale
        if mood is not None and (mood < 1 or mood > 10):
            return False, "Mood score must be between 1 and 10."
        
        # All validation checks passed
        return True, None

    @staticmethod
    def create_log(user_id, data):
        """
        Creates a new daily health log for a user after validating the date format,
        checking for duplicate date entries, and verifying value boundaries.
        
        Parameters:
            user_id (int): The ID of the user creating the log.
            data (dict): Form dictionary with log_date, sleep, water, exercise, etc.
            
        Returns:
            tuple: (bool success, DailyLog instance | str error_message)
        """
        # Parse date string (format YYYY-MM-DD) into a date object
        log_date_str = data.get('log_date')
        try:
            log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return False, "Invalid date format."

        # Check if a log entry for this specific user and date already exists
        existing = DailyLogDAO.get_by_user_and_date(user_id, log_date)
        if existing:
            return False, f"A log already exists for {log_date}."

        # Validate physical metric limits
        is_valid, msg = DailyLogService.validate_log_data(data)
        if not is_valid:
            return False, msg

        # Instantiate a new DailyLog model with provided data
        log = DailyLog(
            user_id=user_id,
            log_date=log_date,
            sleep_hours=data.get('sleep_hours'),
            water_liters=data.get('water_liters'),
            exercise_minutes=data.get('exercise_minutes'),
            mood_score=data.get('mood_score'),
            weight_kg=data.get('weight_kg'),
            notes=data.get('notes')
        )
        # Save to database and return result
        return True, DailyLogDAO.save(log)

    @staticmethod
    def update_log(log_id, user_id, data):
        """
        Updates an existing daily log entry belonging to the specified user.
        
        Parameters:
            log_id (int): ID of the daily log record to update.
            user_id (int): ID of the requesting user (for authorization check).
            data (dict): New field values.
            
        Returns:
            tuple: (bool success, DailyLog instance | str error_message)
        """
        # Retrieve the log and ensure it belongs to this user
        log = DailyLogDAO.get_by_id(log_id)
        if not log or log.user_id != user_id:
            return False, "Log not found or access denied."

        # Validate updated metric bounds
        is_valid, msg = DailyLogService.validate_log_data(data)
        if not is_valid:
            return False, msg

        # Apply updated fields to the model instance
        log.sleep_hours = data.get('sleep_hours')
        log.water_liters = data.get('water_liters')
        log.exercise_minutes = data.get('exercise_minutes')
        log.mood_score = data.get('mood_score')
        log.weight_kg = data.get('weight_kg')
        log.notes = data.get('notes')
        
        # Persist the changes via DAO
        return True, DailyLogDAO.save(log)

    @staticmethod
    def delete_log(log_id, user_id):
        """
        Deletes a daily log record if it belongs to the requesting user.
        
        Parameters:
            log_id (int): ID of the record to delete.
            user_id (int): ID of the user requesting deletion.
            
        Returns:
            tuple: (bool success, str message)
        """
        # Ensure the log exists and user has ownership
        log = DailyLogDAO.get_by_id(log_id)
        if not log or log.user_id != user_id:
            return False, "Log not found or access denied."
        # Remove the record
        DailyLogDAO.delete(log)
        return True, "Log deleted successfully."

    @staticmethod
    def increment_water(user_id, amount_liters):
        """
        Quick-action helper to add a specified amount of water intake for today.
        Creates a new log entry for today if one does not already exist.
        
        Parameters:
            user_id (int): ID of the user logging hydration.
            amount_liters (float): Amount of water to add in liters (e.g. 0.25).
            
        Returns:
            tuple: (bool success, DailyLog instance)
        """
        from datetime import date
        today = date.today()
        # Find today's existing log entry
        log = DailyLogDAO.get_by_user_and_date(user_id, today)
        
        if not log:
            # Create a brand new basic log for today with this water amount
            log = DailyLog(user_id=user_id, log_date=today, water_liters=amount_liters)
        else:
            # Increment the current water total
            log.water_liters = (log.water_liters or 0.0) + amount_liters
            
        # Commit update to database
        return True, DailyLogDAO.save(log)
