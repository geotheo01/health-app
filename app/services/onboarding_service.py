"""
Onboarding Service Module.

This service guides new users through the setup wizard when they first join the app:
1. Calculates recommended daily calorie targets using the Mifflin-St Jeor formula
   (estimating BMR, factoring in physical activity level, and adjusting for weight loss/gain goals).
2. Saves user answers step-by-step across the multi-page wizard:
   - Step 1: Primary health goal (e.g. lose weight, maintain, gain weight)
   - Step 2: Body stats (age, gender, height, weight, target weight)
   - Step 3: Daily lifestyle habits (sleep hours, water intake, activity level)
   - Step 4: Dietary preferences and eating behaviors
   - Step 5: Final confirmed daily and weekly goals
3. Marks the user's onboarding as complete so they can access the full dashboard.
"""

from app.services.profile_service import ProfileService
from app.services.goal_service import GoalService
from app.dao.habit_dao import HabitDAO
from app.models.user_habit import UserHabit
from app.dao.user_dao import UserDAO

class OnboardingService:
    """
    OnboardingService handles the calculations and multi-step data persistence
    needed during the initial user onboarding flow.
    """

    @staticmethod
    def calculate_suggested_calories(profile_data):
        """
        Calculates a scientifically backed daily calorie recommendation based on the user's stats.
        Uses the Mifflin-St Jeor equation to estimate Basal Metabolic Rate (BMR),
        multiplies by an activity factor to get Total Daily Energy Expenditure (TDEE),
        and adjusts by +/- 500 kcal depending on whether they want to lose or gain weight.

        Parameters:
            profile_data (dict): Dictionary with weight_kg, height_cm, age, gender,
                                 activity_level, and health_goal.

        Returns:
            int: Recommended daily calorie target (defaults to 2000 if data is missing).
        """
        # Extract user profile attributes from the provided dictionary
        weight = profile_data.get('weight_kg')
        height = profile_data.get('height_cm')
        age = profile_data.get('age')
        gender = profile_data.get('gender', 'other')
        activity = profile_data.get('activity_level', 'sedentary')
        goal_type = profile_data.get('health_goal', 'maintain_weight')

        # If any of the required core physical stats are missing, return a safe default
        if not all([weight, height, age]):
            return 2000 # Default fallback

        # Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation
        if gender.lower() == 'male':
            # Formula for men: 10*weight(kg) + 6.25*height(cm) - 5*age(y) + 5
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif gender.lower() == 'female':
            # Formula for women: 10*weight(kg) + 6.25*height(cm) - 5*age(y) - 161
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            # Gender-neutral / other: average of male and female constants
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 78 # Average

        # Map activity levels to standard physical activity multipliers
        multipliers = {
            'sedentary': 1.2,           # Little or no exercise
            'lightly_active': 1.375,    # Light exercise 1-3 days/week
            'moderately_active': 1.55,  # Moderate exercise 3-5 days/week
            'very_active': 1.725,       # Hard exercise 6-7 days/week
            'extremely_active': 1.9     # Very hard daily exercise/physical job
        }
        # Calculate Total Daily Energy Expenditure (TDEE)
        tdee = bmr * multipliers.get(activity, 1.2)

        # Adjust calorie intake based on health goal:
        # Subtract ~500 kcal/day to lose approx 0.5 kg/week, or add 500 kcal/day to gain
        if goal_type == 'lose_weight':
            return int(tdee - 500)
        elif goal_type == 'gain_weight':
            return int(tdee + 500)
        else:
            return int(tdee)

    @staticmethod
    def save_step_data(user_id, step, data):
        """
        Processes and saves form data submitted at each step of the onboarding wizard.

        Parameters:
            user_id (int): ID of the currently logged-in user.
            step (int): Wizard step number (1 to 5).
            data (dict): Form data submitted for that step.

        Returns:
            bool: True if data was saved successfully, False if unknown step.
        """
        if step == 1:
            # Step 1: Save the primary health goal (lose weight, maintain, build muscle, etc.)
            return ProfileService.update_or_create_profile(user_id, {'health_goal': data.get('health_goal')})
        
        elif step == 2:
            # Step 2: Save physical body metrics (age, gender, height, current weight)
            ProfileService.update_or_create_profile(user_id, {
                'age': int(data.get('age')),
                'gender': data.get('gender'),
                'height_cm': float(data.get('height_cm')),
                'weight_kg': float(data.get('weight_kg'))
            })
            # Also save target weight into the user's goals if provided
            if data.get('target_weight_kg'):
                success, result = GoalService.update_or_create_goal(user_id, {'target_weight': float(data.get('target_weight_kg'))})
                if not success:
                    raise ValueError(result)
            return True

        elif step == 3:
            # Step 3: Save daily lifestyle factors (exercise activity level, sleep, water intake)
            ProfileService.update_or_create_profile(user_id, {'activity_level': data.get('activity_level')})
            # Look for existing habit row or create a new one for this user
            habit = HabitDAO.get_by_user_id(user_id) or UserHabit(user_id=user_id)
            habit.average_sleep_hours = float(data.get('average_sleep_hours'))
            habit.average_water_liters = float(data.get('average_water_liters'))
            HabitDAO.save(habit)
            return True

        elif step == 4:
            # Step 4: Save behavioral habits (checkboxes for meal skipping, snacking, sleep patterns, etc.)
            habit = HabitDAO.get_by_user_id(user_id) or UserHabit(user_id=user_id)
            habit.skips_meals = 'skips_meals' in data
            habit.late_night_eating = 'late_night_eating' in data
            habit.frequent_snacking = 'frequent_snacking' in data
            habit.sugary_drinks = 'sugary_drinks' in data
            habit.emotional_eating = 'emotional_eating' in data
            habit.low_activity = 'low_activity' in data
            habit.irregular_sleep = 'irregular_sleep' in data
            habit.diet_preference = data.get('diet_preference', 'none')
            HabitDAO.save(habit)
            return True

        elif step == 5:
            # Step 5: Save final target goals (daily calories, water, sleep, and weekly exercise)
            GoalService.update_or_create_goal(user_id, {
                'daily_calorie_goal': int(data.get('daily_calorie_goal')),
                'daily_water_goal': float(data.get('daily_water_goal')),
                'daily_sleep_goal': float(data.get('daily_sleep_goal')),
                'weekly_exercise_goal': int(data.get('weekly_exercise_goal'))
            })
            return True
        
        # Step number was unrecognized
        return False

    @staticmethod
    def complete_onboarding(user_id):
        """
        Marks onboarding as completed for the user in the database.

        Parameters:
            user_id (int): The user's ID.

        Returns:
            bool: True if user was found and updated, False otherwise.
        """
        user = UserDAO.get_by_id(user_id)
        if user:
            user.onboarding_completed = True
            UserDAO.save(user)
            return True
        return False
