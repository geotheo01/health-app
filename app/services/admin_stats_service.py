"""
admin_stats_service.py
Service layer responsible for compiling system-wide statistics and analytics
for the administrator dashboard. Gathers user metrics, activity heatmaps over
the last 30 days, peak activity hours, and role distributions.
"""

from app.dao.user_dao import UserDAO
from app.dao.daily_log_dao import DailyLogDAO
from app.dao.meal_dao import MealDAO
from app.dao.recommendation_dao import RecommendationDAO


class AdminStatsService:
    """
    Service class that aggregates database metrics to provide high-level
    analytical insights for the admin dashboard.
    """

    @staticmethod
    def get_system_stats():
        """
        Gathers and returns a comprehensive dictionary of system statistics,
        including user counts, activity heatmaps, peak logging hours,
        and role breakdowns.
        
        Returns:
            dict: Dictionary containing counts, heatmap series, and peak hour distributions.
        """
        # Local imports to prevent circular references with application models
        from app.models.user import User
        from app.models.daily_log import DailyLog
        from app.models.meal import Meal
        from datetime import date, timedelta
        from collections import defaultdict

        # -------------------------------------------------------------
        # Base system metrics using DAO helper methods
        # -------------------------------------------------------------
        total_users = UserDAO.count_total()
        active_users = UserDAO.count_active()
        inactive_users = UserDAO.count_inactive()
        total_logs = DailyLogDAO.count_total()
        total_meals = MealDAO.count_total()
        total_recommendations = RecommendationDAO.count_total()
        latest_users = UserDAO.get_latest(5)

        # -------------------------------------------------------------
        # 1. Role distribution statistics (Admin vs Standard User)
        # -------------------------------------------------------------
        admin_count = User.query.filter_by(role='admin').count()
        user_count = User.query.filter_by(role='user').count()
        role_stats = {
            'admin': admin_count,
            'user': user_count
        }

        # -------------------------------------------------------------
        # 2. Daily activity heatmap (last 30 days of user actions)
        # -------------------------------------------------------------
        today = date.today()
        start_date = today - timedelta(days=29)  # 30-day window including today
        activity_counts = defaultdict(int)

        # Count daily logs created within the date window
        logs = DailyLog.query.filter(DailyLog.log_date >= start_date).all()
        for l in logs:
            activity_counts[l.log_date.isoformat()] += 1

        # Count meals logged within the date window
        meals = Meal.query.filter(Meal.meal_date >= start_date).all()
        for m in meals:
            activity_counts[m.meal_date.isoformat()] += 1

        # Build a continuous date series so days with 0 activity are still present
        heatmap_data = []
        curr = start_date
        while curr <= today:
            dt_str = curr.isoformat()
            heatmap_data.append({
                'date': dt_str,
                'count': activity_counts[dt_str]
            })
            curr += timedelta(days=1)

        # -------------------------------------------------------------
        # 3. Peak activity hours (0 to 23 hours of the day)
        # -------------------------------------------------------------
        hour_counts = defaultdict(int)
        all_meals = Meal.query.all()
        for m in all_meals:
            if m.created_at:
                hour_counts[m.created_at.hour] += 1

        # Create a list of 24 values corresponding to counts for hour 0 through 23
        peak_hours = [hour_counts[h] for h in range(24)]

        # Package and return all calculated statistics for the template / API
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'total_logs': total_logs,
            'total_meals': total_meals,
            'total_recommendations': total_recommendations,
            'latest_users': latest_users,
            'role_stats': role_stats,
            'heatmap': heatmap_data,
            'peak_hours': peak_hours
        }

