"""
Wellness Service Module.

This service calculates the daily "Wellness Score" (from 0 to 100) for a user.
The overall score is composed of 5 equal categories (max 20 points each):
1. Sleep: hours slept compared against the user's daily sleep goal.
2. Hydration: liters of water drunk compared against the water goal.
3. Exercise: workout minutes compared against daily exercise target.
4. Mood: user's reported mood rating (1-10 scale mapped to 0-20 points).
5. Nutrition: calorie intake proximity to the daily calorie target.

It also generates friendly textual explanations in the user's active language
highlighting why their score is what it is and how they can improve.
"""

from app.utils.translations import translate as _

class WellnessScoreService:
    """
    WellnessScoreService evaluates a user's daily activity, lifestyle metrics,
    and nutritional logs to compute a comprehensive wellness rating.
    """

    @staticmethod
    def calculate(daily_log, total_calories, goal):
        """
        Calculates the comprehensive wellness score out of 100 and builds feedback.

        Parameters:
            daily_log (DailyLog or None): Today's lifestyle log entry (sleep, water, exercise, mood).
            total_calories (float): Total calories consumed from all logged meals today.
            goal (UserGoal or None): The user's target goals.

        Returns:
            dict: Contains total_score (0-100), individual sub-scores (0-20 each),
                  and a localized explanation text.
        """
        # Determine target thresholds from user's goals, or use sensible defaults if not set
        target_sleep = goal.daily_sleep_goal if goal and goal.daily_sleep_goal else 8.0
        target_water = goal.daily_water_goal if goal and goal.daily_water_goal else 2.0
        target_exercise = (goal.weekly_exercise_goal / 7) if goal and goal.weekly_exercise_goal else 30.0
        target_calories = goal.daily_calorie_goal if goal and goal.daily_calorie_goal else 2000

        # Extract current day's actual recorded metrics, safely defaulting to 0 if missing
        actual_sleep = daily_log.sleep_hours if daily_log and daily_log.sleep_hours else 0.0
        actual_water = daily_log.water_liters if daily_log and daily_log.water_liters else 0.0
        actual_exercise = daily_log.exercise_minutes if daily_log and daily_log.exercise_minutes else 0.0
        actual_mood = daily_log.mood_score if daily_log and daily_log.mood_score else 0

        # Calculate individual sub-scores for sleep, hydration, exercise, and mood (max 20 points each)
        sleep_score = min(20.0, 20.0 * (actual_sleep / target_sleep)) if target_sleep > 0 else 0
        water_score = min(20.0, 20.0 * (actual_water / target_water)) if target_water > 0 else 0
        exercise_score = min(20.0, 20.0 * (actual_exercise / target_exercise)) if target_exercise > 0 else 0
        mood_score = 20.0 * (actual_mood / 10.0)

        # Calculate nutrition score based on how close total calories are to the target
        if total_calories > 0 and target_calories > 0:
            # Measure relative percentage difference (error) from target
            error = abs(total_calories - target_calories) / target_calories
            nutrition_score = max(0.0, 20.0 * (1 - error))
        elif total_calories == 0:
            nutrition_score = 0.0 # No meals logged yet today
        else:
            nutrition_score = 10.0 # Neutral score if no calorie target was configured

        # Calculate total combined wellness score rounded to the nearest integer
        total_score = round(sleep_score + water_score + exercise_score + mood_score + nutrition_score)
        
        # Build helpful explanation list describing any factors that brought the score down
        issues = []
        if not daily_log:
            # User hasn't submitted their daily log at all today
            issues.append(_("you haven't filled out your daily health log"))
        else:
            if sleep_score < 10:
                issues.append(_("sleep was below your goal"))
            if water_score < 10:
                issues.append(_("water intake was low"))
            if exercise_score < 10:
                issues.append(_("exercise was below your daily average target"))
            if mood_score < 10 and actual_mood > 0:
                issues.append(_("your mood was reported as low"))
            
            if total_calories == 0:
                issues.append(_("no meals were logged"))
            elif target_calories > 0 and error > 0.2:
                # Calories deviated by more than 20% from target
                if total_calories > target_calories:
                    issues.append(_("calories exceeded your daily target"))
                else:
                    issues.append(_("calories were well below your daily target"))

        # Formulate positive or constructive message
        if not issues:
            explanation = _("Great job! You are hitting all your wellness goals today.")
        else:
            explanation = _("Your score could improve because: ") + ", ".join(issues) + "."

        # Return comprehensive score summary dictionary
        return {
            'total_score': total_score,
            'sleep_score': round(sleep_score),
            'water_score': round(water_score),
            'exercise_score': round(exercise_score),
            'mood_score': round(mood_score),
            'nutrition_score': round(nutrition_score),
            'explanation': explanation
        }
