"""
Meal and MealItem Models
This module defines the database models for food tracking:
- Meal: Represents an overall meal entry (e.g., Breakfast, Lunch) logged by a user.
- MealItem: Represents individual food items that comprise a meal, detailing specific nutritional stats.
"""

from datetime import datetime, timezone
from app import db


class Meal(db.Model):
    """
    Represents a meal logged by a user on a particular date.
    Stores aggregated macronutrients, meal category, optional photo path,
    and AI vision confidence metrics.
    Has a one-to-many relationship with MealItem objects.
    """
    __tablename__ = 'meals'

    # Primary key for the meal record
    id = db.Column(db.Integer, primary_key=True)

    # Reference to the user who logged this meal
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Calendar date when the meal was consumed
    meal_date = db.Column(db.Date, nullable=False)

    # Type/time of meal (e.g., 'breakfast', 'lunch', 'dinner', 'snack')
    meal_type = db.Column(db.String(50), nullable=False)

    # Short description or name of the meal
    title = db.Column(db.String(100), nullable=False)

    # Aggregated nutritional summary for the meal
    total_calories = db.Column(db.Float, default=0.0)
    total_protein = db.Column(db.Float, default=0.0)
    total_carbs = db.Column(db.Float, default=0.0)
    total_fat = db.Column(db.Float, default=0.0)

    # File path or URL to the uploaded meal photo (if user took a photo)
    image_path = db.Column(db.String(255))

    # Confidence score (0.0 to 1.0) returned if detected by AI image recognition
    ai_confidence = db.Column(db.Float)

    # Timestamp when the meal record was created in UTC
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship linking back to User model so user.meals    # Foreign key relationship to the User model
    user = db.relationship('User', backref=db.backref('meals', lazy=True, cascade='all, delete-orphan'))

    # One-to-many relationship with MealItem. Deleting a meal automatically removes its items.
    items = db.relationship('MealItem', backref='meal', lazy=True, cascade="all, delete-orphan")


class MealItem(db.Model):
    """
    Represents an individual food item or ingredient within a logged meal.
    Stores item name, serving size/quantity, and specific macronutrient breakdown.
    """
    __tablename__ = 'meal_items'

    # Primary key for the meal item record
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking the item to its parent meal
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)

    # Name of the food item (e.g., "Oatmeal", "Almond Milk", "Apple")
    food_name = db.Column(db.String(100), nullable=False)

    # Serving size or quantity description (e.g., "1 cup", "150g", "2 slices")
    quantity = db.Column(db.String(50))

    # Individual macronutrient and calorie values for this specific food item
    calories = db.Column(db.Float, default=0.0)
    protein = db.Column(db.Float, default=0.0)
    carbs = db.Column(db.Float, default=0.0)
    fat = db.Column(db.Float, default=0.0)

