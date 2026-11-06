"""
Gemini Advisor Integration Module

This module acts as an external service helper in our application's MVC architecture.
It serves as an interface between the Controller layer (which fetches user metrics 
and health records from the database Models) and Google's Gemini Generative AI API.

The purpose of this component is to aggregate user profile details, daily logs, and meal 
history, generate a dynamically engineered prompt, and query the LLM to return structured, 
personalized health and wellness recommendations formatted in Greek for app localization.
"""

import os
import json
from google import genai
from app.utils.translations import translate as _

class GeminiAdvisor:
    """
    Helper class containing static methods to manage communication with Google's Gemini API 
    and format health recommendations for the user interface.
    """

    @staticmethod
    def analyze(user, goal, recent_logs, recent_meals):
        """
        Analyzes a user's recent logs, meals, profile, and target goals to produce structured 
        AI-generated feedback.

        Parameters:
            user (User): The database User model object containing profile information.
            goal (Goal): The User's target goals (e.g., calories, water, sleep).
            recent_logs (list): A list of recent daily health log ORM objects (last 7 days).
            recent_meals (list): A list of recent meal log ORM objects (last 7 days).

        Returns:
            list[dict]: A list of standardized recommendation dictionaries containing 'category', 
                       'message', and 'explanation'.
        """
        # Verify that the Gemini API key is configured in the environment variables
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            # Fall back to a default static response if API configuration is missing
            return GeminiAdvisor._fallback_response()
            
        try:
            # Initialize the official Google GenAI SDK client
            client = genai.Client(api_key=api_key)
            from google.genai import types as genai_types
            
            # Format data for prompt: Convert log ORM instances into a readable string summary
            logs_text = "\n".join([
                f"Date: {log.log_date}, Sleep: {log.sleep_hours}h, Water: {log.water_liters}L, Exercise: {log.exercise_minutes}m, Mood: {log.mood_score}/10"
                for log in recent_logs
            ]) if recent_logs else "No recent logs."
            
            # Format data for prompt: Convert meal ORM instances into a formatted text list
            meals_text = "\n".join([
                f"Date: {meal.meal_date}, Meal: {meal.title}, Calories: {meal.total_calories}"
                for meal in recent_meals
            ]) if recent_meals else "No recent meals logged."
            
            # Extract profile demographic information safely (defaulting to N/A if missing)
            profile = user.profile if user else None
            user_info = f"Age: {profile.age if profile and profile.age else 'N/A'}, Goal: {profile.health_goal if profile and profile.health_goal else 'N/A'}"
            
            # Extract daily targets or fall back to standard baseline targets
            targets = f"Target Calories: {goal.daily_calorie_goal if goal else 2000}, Target Water: {goal.daily_water_goal if goal else 2.0}L, Target Sleep: {goal.daily_sleep_goal if goal else 8.0}h"

            # Construct the system prompt detailing user metrics and enforcing a strict JSON output schema
            prompt = f"""
You are an expert AI Health & Wellness Advisor.
User Profile: {user_info}
User Targets: {targets}

Recent Daily Logs (last 7 days):
{logs_text}

Recent Meals (last 7 days):
{meals_text}

Analyze the user's data and provide personalized insights in the following strictly structured JSON format:
{{
    "weekly_insight": {{
        "message": "A short, engaging title summarizing a trend you noticed.",
        "explanation": "A 2-3 sentence explanation of the trend (e.g., how their sleep affects their mood or calories)."
    }},
    "daily_actions": [
        {{
            "message": "Actionable task title 1",
            "explanation": "Why they should do this and how it helps their specific goals."
        }},
        {{
            "message": "Actionable task title 2",
            "explanation": "Why they should do this and how it helps their specific goals."
        }},
        {{
            "message": "Actionable task title 3",
            "explanation": "Why they should do this and how it helps their specific goals."
        }}
    ],
    "food_quality": {{
        "message": "Nutritional Quality Assessment",
        "explanation": "A 2-3 sentence assessment of their recent meals. If none, advise them to start logging."
    }}
}}

Important: 
- The response MUST be valid JSON.
- Safety boundaries: You are NOT a doctor. Never provide medical diagnoses, never name diseases the user might have, and never suggest, change or stop medication. Give only general lifestyle, nutrition, hydration, sleep and exercise guidance. If the data or the question suggests a medical issue (e.g. extreme values, symptoms, eating disorders), recommend that the user consult a qualified health professional.
- Provide the content in the language the user would prefer (Greek or English based on the typical context, assume Greek if unsure but Greek text is highly encouraged). Let's output exclusively in Greek to match the app's localization.
- Be encouraging, practical, and highly personalized based on the numbers provided.
"""
            # Call the Gemini API model enforcing JSON MIME-type in response configuration
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type='application/json'
                )
            )
            # Parse the API text response into a native Python dictionary
            data = json.loads(response.text)
            
            # Map JSON to recommendation dictionaries
            # Handle both formats: string values or {message, explanation} objects
            recommendations = []

            # Defensive parsing: handle weekly insight whether it returns a dict or raw string
            if 'weekly_insight' in data:
                wi = data['weekly_insight']
                if isinstance(wi, dict):
                    msg = wi.get('message', 'Weekly Insight')
                    exp = wi.get('explanation', '')
                else:
                    msg = 'Εβδομαδιαία Ανάλυση'
                    exp = str(wi)
                recommendations.append({'category': 'weekly_insight', 'message': msg, 'explanation': exp})

            # Process array of daily action items
            if 'daily_actions' in data:
                for action in data['daily_actions']:
                    if isinstance(action, dict):
                        msg = action.get('message', 'Daily Action')
                        exp = action.get('explanation', '')
                    else:
                        msg = str(action)[:80]
                        exp = str(action)
                    recommendations.append({'category': 'daily_action', 'message': msg, 'explanation': exp})

            # Defensive parsing: handle food quality evaluation section
            if 'food_quality' in data:
                fq = data['food_quality']
                if isinstance(fq, dict):
                    msg = fq.get('message', 'Food Quality Assessment')
                    exp = fq.get('explanation', '')
                else:
                    msg = 'Αξιολόγηση Διατροφής'
                    exp = str(fq)
                recommendations.append({'category': 'food_quality', 'message': msg, 'explanation': exp})

            return recommendations

        except Exception as e:
            # Output stack trace for debugging API errors or parsing failures
            import traceback
            traceback.print_exc()
            print(f"Gemini Advisor Error: {e}")
            # Ensure graceful degradation by providing static feedback if API call fails
            return GeminiAdvisor._fallback_response()

    @staticmethod
    def _fallback_response():
        """
        Generates a default, localized fallback recommendation list when API calls 
        fail or when an API key is not present.

        Returns:
            list[dict]: A list containing localized user instructions.
        """
        return [
            {
                'category': 'daily_action',
                'message': _('Log your daily data'),
                'explanation': _('Please ensure your API key is correct or try again later. For now, focus on logging your meals and water.')
            }
        ]
