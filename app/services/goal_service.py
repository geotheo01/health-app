"""
goal_service.py
Service layer for managing personal wellness and fitness goals.
Handles retrieving current targets and creating or updating goals
(daily calories, daily water, daily sleep, weekly exercise, target weight)
with input validation to prevent negative values.
"""

from app.dao.goal_dao import GoalDAO
from app.models.goal import Goal


class GoalService:
    """
    Service class providing business logic for setting and maintaining user targets.
    """

    @staticmethod
    def get_user_goal(user_id):
        """
        Retrieves the fitness and health targets set by a specific user.
        
        Parameters:
            user_id (int): The ID of the user.
            
        Returns:
            Goal | None: The user's Goal record, or None if none has been set yet.
        """
        # Look up goal entity in database via DAO
        return GoalDAO.get_by_user_id(user_id)

    @staticmethod
    def update_or_create_goal(user_id, data):
        """
        Creates or updates a user's health goals after verifying that all numeric
        targets are non-negative.
        
        Parameters:
            user_id (int): The ID of the user.
            data (dict): Dictionary of targets to update (e.g., daily_calorie_goal, target_weight).
            
        Returns:
            tuple: (bool success, Goal instance | str error_message)
        """
        # Validation: check that none of the provided numerical targets are negative
        for key, val in data.items():
            if val is not None and val < 0:
                # Format snake_case key into user-friendly title (e.g. "Daily Calorie Goal")
                name = key.replace('_', ' ').title()
                return False, f"{name} must be a positive number."
            if key == 'target_weight' and val is not None:
                if not (40 <= val <= 230):
                    return False, "Ο στόχος βάρους πρέπει να είναι μεταξύ 40 και 230 kg."

        # Fetch existing goal record or initialize a new one if this is the user's first time
        goal = GoalDAO.get_by_user_id(user_id)
        if not goal:
            goal = Goal(user_id=user_id)
        
        # Selectively update each target field if included in the incoming data payload
        if 'daily_calorie_goal' in data:
            goal.daily_calorie_goal = data.get('daily_calorie_goal')
        if 'daily_water_goal' in data:
            goal.daily_water_goal = data.get('daily_water_goal')
        if 'daily_sleep_goal' in data:
            goal.daily_sleep_goal = data.get('daily_sleep_goal')
        if 'weekly_exercise_goal' in data:
            goal.weekly_exercise_goal = data.get('weekly_exercise_goal')
        if 'target_weight' in data:
            goal.target_weight = data.get('target_weight')
        
        # Persist goal record to the database
        return True, GoalDAO.save(goal)
