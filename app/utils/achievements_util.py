"""
Achievements & Gamification Utility
-----------------------------------
This module handles computing user achievements, streaks, and challenges.
It analyzes a user's logged meals and daily wellness logs to determine if they
have unlocked specific milestone badges (such as 'Hydration Hero', 'Sleep King',
'Early Bird', 'Streak Master', etc.) and tracks progress toward ongoing health challenges.
"""

from datetime import datetime, timedelta
from app.models.daily_log import DailyLog
from app.models.meal import Meal
from app.utils.translations import translate as _


def calculate_achievements(user):
    """
    Evaluates a user's entire logging history to calculate unlocked badges, streaks, and challenge progress.

    Parameters:
        user (User): The user object whose achievements and logs are being analyzed.

    Returns:
        dict: A dictionary containing:
            - 'badges': list of badge definitions with unlock statuses and criteria strings.
            - 'challenges': list of ongoing gamified challenges with progress percentages.
            - 'unlocked_count': integer number of unlocked badges.
            - 'total_count': total number of available badges.
            - 'max_streak': the longest consecutive logging streak in days.
    """
    # Step 1: Fetch all historical health logs and meals for this user in ascending chronological order
    logs = DailyLog.query.filter_by(user_id=user.id).order_by(DailyLog.log_date.asc()).all()
    meals = Meal.query.filter_by(user_id=user.id).order_by(Meal.meal_date.asc()).all()

    # Step 2: Establish baseline targets from user's custom goals (or fall back to sensible defaults)
    water_target = 2.0  # Default target: 2 liters of water
    sleep_target = 8.0  # Default target: 8 hours of sleep
    if user.goal:
        if user.goal.daily_water_goal:
            water_target = user.goal.daily_water_goal
        if user.goal.daily_sleep_goal:
            sleep_target = user.goal.daily_sleep_goal

    # Step 3: Evaluate criteria for individual badges
    
    # Badge 1: Hydration Hero - unlocked if any log reaches or exceeds daily water goal
    hydration_hero = any((log.water_liters or 0.0) >= water_target for log in logs)

    # Badge 2: Sleep King - unlocked if any log meets or exceeds daily sleep target
    sleep_king = any((log.sleep_hours or 0.0) >= sleep_target for log in logs)

    # Badge 3: Mindfulness - unlocked if mood score was rated 8 or higher on a 1-10 scale
    mindfulness = any((log.mood_score or 0) >= 8 for log in logs)

    # Badge 4: Consistency - unlocked if user has recorded 5 or more total entries (logs + meals)
    consistency = (len(logs) + len(meals)) >= 5

    # Badge 5: Early Bird - unlocked if user logged a breakfast meal before 10:00 AM local time
    early_bird = False
    for meal in meals:
        if meal.meal_type.lower() == 'breakfast':
            # SQLite stores datetime in UTC, so we convert to local time (UTC+3 for Greece)
            if meal.created_at:
                local_hour = meal.created_at.hour
                local_hour = (local_hour + 3) % 24
                # Check if breakfast was eaten / recorded before 10 AM
                if local_hour < 10:
                    early_bird = True
                    break

    # Badge 6: Streak Master - tracks whether the user has logged for 3 or more consecutive days
    # Collect all unique dates on which the user made an entry (either a health log or a meal)
    unique_dates = set()
    for log in logs:
        unique_dates.add(log.log_date)
    for meal in meals:
        unique_dates.add(meal.meal_date)
    
    # Sort dates sequentially to compute the longest continuous day streak
    sorted_dates = sorted(list(unique_dates))
    max_streak = 0
    current_streak = 0
    prev_date = None
    
    for d in sorted_dates:
        if prev_date is None:
            # First recorded day starts a streak of 1
            current_streak = 1
        elif d == prev_date + timedelta(days=1):
            # Consecutive consecutive day found -> increment streak counter
            current_streak += 1
        elif d == prev_date:
            # Same calendar day with multiple entries -> do not increment
            pass
        else:
            # Streak was broken; record max if higher, then reset streak
            if current_streak > max_streak:
                max_streak = current_streak
            current_streak = 1
        prev_date = d
        
    # Check one last time after the loop finishes in case the final streak was the longest
    if current_streak > max_streak:
        max_streak = current_streak
        
    # User gets the Streak Master badge if their streak reached at least 3 days
    streak_master = max_streak >= 3

    # Step 4: Define badge objects with translated metadata, visual styling, and unlock status
    badges = [
        {
            'id': 'streak_master',
            'title': _('Streak Master'),
            'description': _('Log logs or meals for 3+ consecutive days'),
            'icon': 'flame',
            'unlocked': streak_master,
            'color': 'linear-gradient(135deg, #ff416c, #ff4b2b)',
            'criteria': _('3 consecutive days active (Current: {streak} days)').format(streak=max_streak)
        },
        {
            'id': 'hydration_hero',
            'title': _('Hydration Hero'),
            'description': _('Meet your daily water goal at least once'),
            'icon': 'droplet',
            'unlocked': hydration_hero,
            'color': 'linear-gradient(135deg, #2193b0, #6dd5ed)',
            'criteria': _('Log >= {target}L of water in one day').format(target=water_target)
        },
        {
            'id': 'sleep_king',
            'title': _('Sleep King'),
            'description': _('Meet your daily sleep goal of 8+ hours'),
            'icon': 'moon',
            'unlocked': sleep_king,
            'color': 'linear-gradient(135deg, #1f4068, #162447)',
            'criteria': _('Log >= {target}h of sleep in one day').format(target=sleep_target)
        },
        {
            'id': 'early_bird',
            'title': _('Early Bird'),
            'description': _('Log breakfast early in the morning'),
            'icon': 'sunrise',
            'unlocked': early_bird,
            'color': 'linear-gradient(135deg, #f12711, #f5af19)',
            'criteria': _('Log breakfast before 10:00 AM')
        },
        {
            'id': 'mindfulness',
            'title': _('Mindfulness'),
            'description': _('Report an excellent mood score of 8 or above'),
            'icon': 'smile',
            'unlocked': mindfulness,
            'color': 'linear-gradient(135deg, #11998e, #38ef7d)',
            'criteria': _('Mood score >= 8/10')
        },
        {
            'id': 'consistency',
            'title': _('Consistency'),
            'description': _('Log 5 or more total activities'),
            'icon': 'award',
            'unlocked': consistency,
            'color': 'linear-gradient(135deg, #8a2387, #e94057, #f27121)',
            'criteria': _('Total logs + meals >= 5 (Current: {total})').format(total=len(logs) + len(meals))
        }
    ]
    
    # Step 5: Compute progress percentages for ongoing habit challenges (capped at 100%)
    challenges = [
        {
            'title': _('Hydration Challenge'),
            'description': _('Drink water for 3 consecutive days to establish a habit.'),
            'progress': min(100, int((max_streak / 3.0) * 100)) if hydration_hero else 0,
            'icon': 'droplet'
        },
        {
            'title': _('Consistency Challenge'),
            'description': _('Build consistent logging habits by logging 5 meals or logs.'),
            'progress': min(100, int(((len(logs) + len(meals)) / 5.0) * 100)),
            'icon': 'check-circle'
        }
    ]

    # Step 6: Return summary results
    return {
        'badges': badges,
        'challenges': challenges,
        'unlocked_count': sum(1 for b in badges if b['unlocked']),
        'total_count': len(badges),
        'max_streak': max_streak
    }

