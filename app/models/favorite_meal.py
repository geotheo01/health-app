"""
Favorite Meal Model
This module defines the FavoriteMeal database model, which allows users to save
and reuse their favorite meals or recipes with pre-calculated nutritional macros.
"""

from datetime import datetime
from app import db


class FavoriteMeal(db.Model):
    """
    Represents a saved or bookmarked meal template created by a user.
    Stores aggregated macronutrients (calories, protein, carbs, fat) and
    an optional serialized list of food items for quick re-logging.
    """
    __tablename__ = 'favorite_meals'

    # Primary key for uniquely identifying each saved favorite meal
    id = db.Column(db.Integer, primary_key=True)

    # Reference to the user who saved this favorite meal
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # User-defined name or title of the meal (e.g., "Protein Oatmeal")
    title = db.Column(db.String(100), nullable=False)

    # Meal category such as breakfast, lunch, dinner, or snack
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack

    # Aggregated nutritional values (macronutrients) for quick reference
    total_calories = db.Column(db.Float, default=0.0)
    total_protein = db.Column(db.Float, default=0.0)
    total_carbs = db.Column(db.Float, default=0.0)
    total_fat = db.Column(db.Float, default=0.0)

    # Serialized JSON text containing the list of individual food items and quantities
    # Stored as text for the MVP to keep the structure simple and flexible
    items_json = db.Column(db.Text, nullable=True)

    # Timestamp when this favorite meal was created (defaults to current UTC time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """
        Returns a friendly string representation for debugging and logging.
        """
        return f'<FavoriteMeal {self.title}>'

