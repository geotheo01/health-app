"""
chatbot_service.py
Service layer for the AI Health & Wellness Coach chatbot.
Handles receiving user messages, fetching current health context (goals, daily logs, meals),
querying the Google Gemini API for personalized conversational coaching,
and providing a graceful rule-based fallback if the API is unreachable or unconfigured.
"""

from app.dao.chat_dao import ChatDAO
from app.models.chat_message import ChatMessage
from app.dao.daily_log_dao import DailyLogDAO
from app.dao.meal_dao import MealDAO
from app.dao.goal_dao import GoalDAO
from datetime import date
from app.utils.translations import translate as _
import os


class ChatbotService:
    """
    Service class responsible for managing chatbot dialogues and message processing.
    """

    @staticmethod
    def process_message(user_id, user_message):
        """
        Processes an incoming user chat message, persists it, prepares context from
        the user's daily activity and goals, queries Gemini (or fallback logic),
        and saves and returns the assistant's response.
        
        Parameters:
            user_id (int): ID of the user sending the message.
            user_message (str): Text content of the user's message.
            
        Returns:
            ChatMessage: The persisted assistant reply message model.
        """
        # Step 1: Save the incoming user message to the database
        u_msg = ChatMessage(user_id=user_id, sender='user', message=user_message)
        ChatDAO.save(u_msg)

        # Step 2: Retrieve today's health metrics and user targets for contextual prompt building
        today = date.today()
        daily_log = DailyLogDAO.get_by_user_and_date(user_id, today)
        meals = MealDAO.get_user_meals_by_date(user_id, today)
        goal = GoalDAO.get_by_user_id(user_id)

        # Calculate totals or assign sensible defaults if logs are missing
        total_calories = sum(m.total_calories for m in meals) if meals else 0
        water = daily_log.water_liters if daily_log and daily_log.water_liters else 0.0
        exercise = daily_log.exercise_minutes if daily_log and daily_log.exercise_minutes else 0
        sleep = daily_log.sleep_hours if daily_log and daily_log.sleep_hours else 0.0
        mood_score = daily_log.mood_score if daily_log and daily_log.mood_score else 'Not logged'

        # Fetch user profile to personalize advice (age, weight, height, goal)
        from app.dao.user_dao import UserDAO
        user = UserDAO.get_by_id(user_id)
        profile = user.profile if user else None

        # Build a readable summary of meals logged today
        meals_text = ""
        if meals:
            meals_text = ", ".join([f"{m.title} ({m.total_calories} kcal)" for m in meals])
        else:
            meals_text = "No meals logged yet today"

        # Step 3: Construct the system prompt for the Gemini AI coach
        system_prompt = f"""
You are an expert AI Health & Wellness Coach for the "Smart Health Tracker" application.
You are helping the currently logged-in user of the application.

USER PHYSICAL PROFILE:
- Age: {profile.age if (profile and profile.age) else 'Not set'} years
- Biological Sex: {profile.gender if (profile and profile.gender) else 'Not set'}
- Height: {profile.height_cm if (profile and profile.height_cm) else 'Not set'} cm
- Current Weight: {profile.weight_kg if (profile and profile.weight_kg) else 'Not set'} kg
- Activity Level: {profile.activity_level if (profile and profile.activity_level) else 'Not set'}
- Main Health Goal: {profile.health_goal if (profile and profile.health_goal) else 'Not set'}

USER DAILY & WEEKLY GOALS:
- Daily Calorie Target: {goal.daily_calorie_goal if (goal and goal.daily_calorie_goal) else 2000} kcal
- Daily Water Target: {goal.daily_water_goal if (goal and goal.daily_water_goal) else 2.0} L
- Daily Sleep Target: {goal.daily_sleep_goal if (goal and goal.daily_sleep_goal) else 8.0} hours
- Weekly Exercise Target: {goal.weekly_exercise_goal if (goal and goal.weekly_exercise_goal) else 150} minutes
- Target Weight: {goal.target_weight if (goal and goal.target_weight) else 'Not set'} kg

USER TODAY'S RECORDED METRICS (Date: {today.isoformat()}):
- Water Intake: {water} L
- Sleep Duration: {sleep} hours
- Exercise Done: {exercise} minutes
- Mood Score: {mood_score}/10
- Logged Meals: {meals_text}

INSTRUCTIONS:
1. You are a friendly, encouraging, professional, and knowledgeable personal health advisor.
2. The user can chat with you in either Greek or English. You MUST reply in the same language the user uses for their message (e.g. if they query in Greek, write fully in Greek; if in English, write in English).
3. Be conversational, highly practical, and motivating. Leverage the user's today's metrics and profile in your answers whenever they ask for progress, recommendations, recipes, or health logs.
4. If they ask how they are doing, provide an encouraging summary based on their daily targets and metrics.
5. Keep your responses relatively concise and focused on healthy habit building. Use emojis appropriately to make it engaging!
6. SAFETY BOUNDARIES: You are NOT a doctor. Never provide medical diagnoses, never name diseases the user might have, and never suggest, change or stop medication. Give only general lifestyle, nutrition, hydration, sleep and exercise guidance. If the user describes symptoms, a medical condition, extreme values or signs of disordered eating, kindly recommend that they consult a qualified health professional (doctor or registered dietitian).
"""

        response_text = None

        # Step 4: Try calling the Google Gemini generative AI API
        try:
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("No Gemini API key configured.")

            from google import genai
            from google.genai import types as genai_types
            client = genai.Client(api_key=api_key)

            # Build conversation history as text for context (up to last 10 messages)
            chat_history = ChatDAO.get_user_chat_history(user_id)
            history_text = ""
            for msg in chat_history[:-1][-10:]:
                role_label = "User" if msg.sender == 'user' else "Assistant"
                history_text += f"{role_label}: {msg.message}\n"

            # Construct full prompt including system instructions, history and new message
            full_prompt = f"{system_prompt}\n\nConversation so far:\n{history_text}\nUser: {user_message}\nAssistant:"

            # Call Gemini using generate_content (same stable method as the advisor)
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=full_prompt
            )
            response_text = response.text

        except Exception as e:
            # Step 5: Fallback to rule-based generation if API call fails or key is not set
            import traceback
            traceback.print_exc()
            print(f"Gemini API Error: {e}")
            
            from app.services.dashboard_service import DashboardService
            streak = DashboardService.calculate_streak(user_id)
            
            # Form basic summary string with translation support
            response_text = _("Today you've consumed {total_calories} calories, drank {water}L of water, and did {exercise} minutes of exercise.", total_calories=total_calories, water=water, exercise=exercise)
            
            # Add streak encouragement if greater than 1 day
            if streak > 1:
                response_text = _("Keep it up! You're on a {streak}-day streak! 🔥 ", streak=streak) + response_text
            
            # Check hydration progress against daily target
            if goal:
                water_goal = goal.daily_water_goal or 2.0
                if water >= water_goal:
                    response_text += _(" ✨ You've reached your hydration goal for today!")
                else:
                    rem = round(max(0, water_goal - water), 1)
                    response_text += _(" You need about {rem}L more to hit your goal.", rem=rem)
            
            # Simple keyword matching for greetings or advice requests
            msg_lower = user_message.lower()
            if 'hello' in msg_lower or 'hi' in msg_lower or 'γεια' in msg_lower:
                response_text = _("Hello! I'm your AI health coach. ") + response_text
            elif 'advice' in msg_lower or 'tips' in msg_lower or 'συμβουλ' in msg_lower:
                if total_calories > (goal.daily_calorie_goal if goal else 2000):
                    response_text += _(" I noticed you're over your calorie goal. Maybe try a light walk this evening?")
                elif water < (goal.daily_water_goal if goal else 2.0):
                    response_text += _(" Try drinking a large glass of water now to stay hydrated.")

        # Step 6: Persist the assistant's generated response to the database
        a_msg = ChatMessage(user_id=user_id, sender='assistant', message=response_text)
        ChatDAO.save(a_msg)

        return a_msg

    @staticmethod
    def get_chat_history(user_id):
        """
        Fetch all chat messages belonging to a given user.
        
        Parameters:
            user_id (int): The ID of the user.
            
        Returns:
            list[ChatMessage]: Chronological list of past messages.
        """
        # Retrieve message log from DAO
        return ChatDAO.get_user_chat_history(user_id)

