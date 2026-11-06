"""
History Service Module.

This service file is responsible for gathering and organizing a user's past health data.
It collects daily lifestyle logs (like water, sleep, exercise, weight) and meal logs
over a given period (such as the past 7 days, past 30 days, or a custom date range)
and compiles them into an organized daily timeline for charts and history views.
"""

from app.dao.daily_log_dao import DailyLogDAO
from app.dao.meal_dao import MealDAO
from datetime import datetime, timedelta

class HistoryService:
    """
    HistoryService provides helper methods to aggregate historical logs and meals
    for a specific user so they can view their progress over time.
    """

    @staticmethod
    def get_history_data(user_id, date_range, start_date_str=None, end_date_str=None):
        """
        Retrieves user logs and meals within the requested time frame and groups them by day.

        Parameters:
            user_id (int): ID of the user whose history is being fetched.
            date_range (str): Quick filter option ('7days', '30days', or 'custom').
            start_date_str (str, optional): Custom start date string in 'YYYY-MM-DD' format.
            end_date_str (str, optional): Custom end date string in 'YYYY-MM-DD' format.

        Returns:
            dict: Contains 'start_date', 'end_date', and a list 'history' of daily aggregated records.
        """
        # Get today's calendar date to base our ranges on
        today = datetime.today().date()
        
        # Decide the start and end dates based on the selected range filter
        if date_range == '7days':
            # Past 7 days (including today)
            start_date = today - timedelta(days=6)
            end_date = today
        elif date_range == '30days':
            # Past 30 days (including today)
            start_date = today - timedelta(days=29)
            end_date = today
        elif date_range == 'custom' and start_date_str and end_date_str:
            # Parse custom dates provided by the user
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                # If date format is invalid, fall back safely to the last 7 days
                start_date = today - timedelta(days=6)
                end_date = today
        else:
            # Default fallback if nothing matched: last 7 days
            start_date = today - timedelta(days=6)
            end_date = today

        # Fetch the daily wellness logs and meals from the database for this date window
        logs = DailyLogDAO.get_user_logs_in_range(user_id, start_date, end_date)
        meals = MealDAO.get_user_meals_in_range(user_id, start_date, end_date)

        # Create a dictionary map keyed by date string so that every single day in the range
        # has an entry, even if the user didn't log anything on that day
        history_map = {}
        
        current = start_date
        while current <= end_date:
            history_map[current.isoformat()] = {
                'date': current,
                'log': None,
                'meals': [],
                'total_calories': 0.0,
                'water': 0.0,
                'sleep': 0.0,
                'exercise': 0,
                'weight_kg': None
            }
            # Move forward one day at a time
            current += timedelta(days=1)

        # Merge daily logs into our history map
        for log in logs:
            date_str = log.log_date.isoformat()
            if date_str in history_map:
                history_map[date_str]['log'] = log
                history_map[date_str]['water'] = log.water_liters or 0.0
                history_map[date_str]['sleep'] = log.sleep_hours or 0.0
                history_map[date_str]['exercise'] = log.exercise_minutes or 0
                history_map[date_str]['weight_kg'] = log.weight_kg

        # Merge meal logs into our history map and sum total calories for that day
        for meal in meals:
            date_str = meal.meal_date.isoformat()
            if date_str in history_map:
                history_map[date_str]['meals'].append(meal)
                history_map[date_str]['total_calories'] += meal.total_calories or 0.0

        # Convert dictionary values to a list and sort by date descending (newest day first)
        history_list = [v for k, v in history_map.items()]
        history_list.sort(key=lambda x: x['date'], reverse=True)

        # Return the final compiled history dictionary
        return {
            'start_date': start_date,
            'end_date': end_date,
            'history': history_list
        }
