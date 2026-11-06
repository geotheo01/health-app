"""
Rule-Based Health Advisor Service

This module serves as a core domain logic service in the application's Model-View-Controller (MVC)
architecture. It acts as an expert system helper that evaluates a user's daily logged health metrics
against their target wellness goals. Based on heuristic rules, it generates contextual, localized
recommendations to assist users in meeting their daily lifestyle targets.
"""

from app.utils.translations import translate as _

class RuleBasedAdvisor:
    """
    A rule-based recommendation engine for health and wellness tracking.
    
    Evaluates logged daily activities (sleep, water intake, exercise, nutrition, mood)
    against personalized user goals and returns actionable feedback.
    """

    @staticmethod
    def analyze(daily_log, total_calories, goal):
        """
        Analyzes a single day's health metrics against defined goal targets.

        Parameters:
            daily_log (DailyLog or None): Database record containing daily tracked metrics.
            total_calories (float or int): Pre-calculated total calorie intake for the day.
            goal (Goal or None): User's target goals instance containing thresholds.

        Returns:
            list[dict]: A list of localized recommendation objects containing 'category',
                        'message', and detailed 'explanation'.
        """
        recommendations = []
        
        # Define baseline target thresholds using safety fallbacks if user goals are missing or partial
        target_sleep = goal.daily_sleep_goal if goal and goal.daily_sleep_goal else 8.0
        target_water = goal.daily_water_goal if goal and goal.daily_water_goal else 2.0
        # Convert weekly exercise target into a daily average target (weekly goal divided by 7 days)
        target_exercise = (goal.weekly_exercise_goal / 7) if goal and goal.weekly_exercise_goal else 30.0
        target_calories = goal.daily_calorie_goal if goal and goal.daily_calorie_goal else 2000

        # --- Evaluate Sleep Duration ---
        # Safely extract logged sleep hours, defaulting to zero if unrecorded
        actual_sleep = daily_log.sleep_hours if daily_log and daily_log.sleep_hours else 0.0
        if actual_sleep < target_sleep:
            recommendations.append({
                'category': 'sleep',
                'message': _('Improve your sleep schedule.'),
                'explanation': _('You slept {actual_sleep}h, which is below your goal of {target_sleep}h. Try going to bed 30 minutes earlier tonight.', actual_sleep=actual_sleep, target_sleep=target_sleep)
            })

        # --- Evaluate Hydration (Water Intake) ---
        # Compare logged liters of water against daily target
        actual_water = daily_log.water_liters if daily_log and daily_log.water_liters else 0.0
        if actual_water < target_water:
            recommendations.append({
                'category': 'water',
                'message': _('Drink more water.'),
                'explanation': _('You drank {actual_water}L, which is below your goal of {target_water}L. Keep a water bottle nearby.', actual_water=actual_water, target_water=target_water)
            })

        # --- Evaluate Daily Exercise ---
        # Compare physical activity duration against calculated daily exercise threshold
        actual_exercise = daily_log.exercise_minutes if daily_log and daily_log.exercise_minutes else 0.0
        if actual_exercise < target_exercise:
            recommendations.append({
                'category': 'exercise',
                'message': _('Get moving today.'),
                'explanation': _('You exercised {actual_exercise} mins, below your target of {round_target_exercise} mins. Consider a short walk.', actual_exercise=actual_exercise, round_target_exercise=round(target_exercise))
            })

        # --- Evaluate Caloric Intake ---
        # Trigger dynamic warning if total calories consumed exceed the allowed ceiling
        if target_calories > 0 and total_calories > target_calories:
            recommendations.append({
                'category': 'nutrition',
                'message': _('Consider a lighter next meal.'),
                'explanation': _('You consumed {total_calories} kcal, exceeding your daily target of {target_calories} kcal. Focus on protein and vegetables for the rest of the day.', total_calories=total_calories, target_calories=target_calories)
            })
            
        # --- Evaluate Emotional Well-being (Mood Score) ---
        # Low mood scores (1-4 on a 10-point scale) prompt a self-care suggestion
        actual_mood = daily_log.mood_score if daily_log and daily_log.mood_score else 0
        if actual_mood > 0 and actual_mood <= 4:
            recommendations.append({
                'category': 'mood',
                'message': _('Take some time for yourself.'),
                'explanation': _('Your mood is low today. Taking a few minutes to breathe deeply or do something you enjoy might help.')
            })

        return recommendations
