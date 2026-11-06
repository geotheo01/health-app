"""
Recommendation Service Module.

This service generates and retrieves personalized daily health recommendations
for users using the Gemini AI advisor.
It gathers the user's past 7 days of lifestyle logs, recent meals, and fitness
goals, passes them to GeminiAdvisor to generate smart actionable tips, and saves
them to the database so users can read them on their dashboard.
"""

from app.ai.gemini_advisor import GeminiAdvisor
from app.dao.recommendation_dao import RecommendationDAO
from app.dao.daily_log_dao import DailyLogDAO
from app.dao.meal_dao import MealDAO
from app.dao.goal_dao import GoalDAO
from app.models.recommendation import Recommendation
from datetime import date, timedelta

class RecommendationService:
    """
    RecommendationService handles generating and retrieving AI-driven
    wellness and nutritional recommendations for users.
    """

    @staticmethod
    def generate_daily_recommendations(user_id):
        """
        Gathers recent user history and asks Gemini AI to produce daily tips.
        Replaces any previously generated recommendations for today.

        Parameters:
            user_id (int): The ID of the user requesting recommendations.

        Returns:
            list[Recommendation]: Newly created recommendation objects for today.
        """
        # Determine the date range: today and the preceding 7 days
        today = date.today()
        start_date = today - timedelta(days=7)
        
        # Gather 7 days of data
        from app.dao.user_dao import UserDAO
        user = UserDAO.get_by_id(user_id)
        recent_logs = DailyLogDAO.get_user_logs_in_range(user_id, start_date, today)
        recent_meals = MealDAO.get_user_meals_in_range(user_id, start_date, today)
        goal = GoalDAO.get_by_user_id(user_id)
        
        # Analyze using Gemini advisor
        analysis = GeminiAdvisor.analyze(user, goal, recent_logs, recent_meals)
        
        # Replace old recommendations for today to avoid stale or duplicated advice
        RecommendationDAO.delete_for_user_and_date(user_id, today)
        
        # Convert the AI advice dictionaries into Recommendation model objects
        recs = []
        for item in analysis:
            recs.append(Recommendation(
                user_id=user_id,
                recommendation_date=today,
                category=item['category'],
                message=item['message'],
                explanation=item['explanation']
            ))
            
        # Save all new recommendations to the database in batch
        if recs:
            RecommendationDAO.save_all(recs)
            
        return recs

    @staticmethod
    def get_user_recommendations(user_id):
        """
        Retrieves already generated recommendations for the user for today's date.

        Parameters:
            user_id (int): The ID of the user.

        Returns:
            list[Recommendation]: List of Recommendation models for today.
        """
        today = date.today()
        # Query DAO for today's recommendations
        return RecommendationDAO.get_by_user_and_date(user_id, today)
