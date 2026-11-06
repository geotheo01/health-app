"""
dashboard_service.py
Service layer responsible for assembling data shown on the user dashboard.
Includes calculating active daily streaks, aggregating today's macronutrient
intake from logged meals, fetching daily goals, and triggering wellness score calculations.
"""

from app.dao.daily_log_dao import DailyLogDAO
from app.dao.meal_dao import MealDAO
from app.dao.goal_dao import GoalDAO
from datetime import date


class DashboardService:
    """
    Service class providing analytical summaries for the home/dashboard view.
    """

    @staticmethod
    def calculate_streak(user_id):
        """
        Calculates the consecutive active day streak for a user.
        A day is considered active if the user has either submitted a daily log
        or recorded at least one meal. If the user hasn't logged anything today yet,
        the streak is preserved if they logged yesterday.
        
        Parameters:
            user_id (int): The ID of the user.
            
        Returns:
            int: The number of consecutive days in the current streak.
        """
        from datetime import date, timedelta
        today = date.today()
        streak = 0
        current_date = today
        
        while True:
            # A day counts as active if there is a daily log OR at least one meal logged
            log = DailyLogDAO.get_by_user_and_date(user_id, current_date)
            meals = MealDAO.get_user_meals_by_date(user_id, current_date)
            
            if log or (meals and len(meals) > 0):
                # Day is active: increment streak count and step one day backward
                streak += 1
                current_date -= timedelta(days=1)
            else:
                # If today has no logs yet, the user still has time; do not break streak
                if current_date == today:
                    # Check yesterday instead
                    current_date -= timedelta(days=1)
                    continue
                # If any past day was missed, the streak ends
                break
        return streak

    @staticmethod
    def get_dashboard_data(user_id):
        """
        Collects all necessary data components to render the user dashboard,
        including today's meals, macro totals, water/sleep logs, wellness score,
        targets, and streak.
        
        Parameters:
            user_id (int): The ID of the user.
            
        Returns:
            dict: Context dictionary populated with all dashboard statistics.
        """
        today = date.today()
        
        # Query database for today's logs and current targets
        daily_log = DailyLogDAO.get_by_user_and_date(user_id, today)
        meals = MealDAO.get_user_meals_by_date(user_id, today)
        goal = GoalDAO.get_by_user_id(user_id)
        
        # Calculate daily nutrition totals across all meals logged today
        total_calories = sum(meal.total_calories for meal in meals)
        total_protein = sum(meal.total_protein for meal in meals)
        total_carbs = sum(meal.total_carbs for meal in meals)
        total_fat = sum(meal.total_fat for meal in meals)
        
        # Compute holistic wellness score using the dedicated wellness service
        from app.services.wellness_service import WellnessScoreService
        wellness = WellnessScoreService.calculate(daily_log, total_calories, goal)
        
        # Compute the user's active logging streak
        streak = DashboardService.calculate_streak(user_id)
        
        # Package and return all data points for the view template
        return {
            'today': today,
            'daily_log': daily_log,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'goal': goal,
            'wellness': wellness,
            'streak': streak
        }
