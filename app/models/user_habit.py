"""
User Habit Model
----------------
This module defines the UserHabit SQLAlchemy model.
It captures behavioral habits and lifestyle preferences collected during
user onboarding or profile updates (such as meal skipping, late-night eating,
hydration habits, and dietary choices). These habits help power personalized
health insights and smart suggestions.
"""

from app import db


class UserHabit(db.Model):
    """
    Stores behavioral lifestyle habits and dietary preferences for a user.
    Maintains a 1-to-1 relationship with the User model.
    """
    # Name of the database table
    __tablename__ = 'user_habits'

    # Primary key identifier for the habit entry
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key referencing the user (unique=True ensures a strict 1-to-1 link)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Behavioral Habit Flags (Booleans tracking potential areas for health improvement)
    skips_meals = db.Column(db.Boolean, default=False)        # True if the user frequently skips breakfast/meals
    late_night_eating = db.Column(db.Boolean, default=False)  # True if the user often eats right before sleep
    frequent_snacking = db.Column(db.Boolean, default=False)  # True if user snacks throughout the day
    sugary_drinks = db.Column(db.Boolean, default=False)      # True if sodas or sugary beverages are regularly consumed
    emotional_eating = db.Column(db.Boolean, default=False)   # True if user tends to eat when stressed or emotional
    low_activity = db.Column(db.Boolean, default=False)       # True if daily physical movement is very minimal
    irregular_sleep = db.Column(db.Boolean, default=False)    # True if bedtime and wake-up times fluctuate wildly
    
    # Baseline lifestyle preferences and typical averages
    diet_preference = db.Column(db.String(50), default='none')  # e.g., 'none', 'vegetarian', 'vegan', 'keto'
    average_sleep_hours = db.Column(db.Float)                   # Self-reported typical sleep per night in hours
    average_water_liters = db.Column(db.Float)                  # Self-reported typical water intake per day in liters
    
    # Relationship back to the    # 1-to-1 relationship with the primary User model
    user = db.relationship('User', backref=db.backref('habits', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        """
        String representation of the UserHabit model for debugging and console logs.
        """

