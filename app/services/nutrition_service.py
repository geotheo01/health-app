"""
Nutrition Service Module.

This service manages the nutrition database stored locally in a JSON file
(`data/nutrition_db.json`). It provides helper methods to read food reference
data (calories, protein, carbs, fat), add new food items, update existing items,
and delete items from the food database.
"""

import os
import json
from flask import current_app

class NutritionService:
    """
    NutritionService handles CRUD operations for the local food nutrition
    reference database loaded from a JSON file.
    """

    @staticmethod
    def _get_db_path():
        """
        Helper method to get the absolute path to the nutrition JSON file.

        Returns:
            str: Path to 'nutrition_db.json' located in the app's 'data' folder.
        """
        return os.path.join(current_app.root_path, 'data', 'nutrition_db.json')

    @staticmethod
    def get_all_foods():
        """
        Reads all food entries from the JSON database file.

        Returns:
            dict: Dictionary of food keys and their nutrition information.
        """
        path = NutritionService._get_db_path()
        # If the file does not exist yet, return an empty dictionary
        if not os.path.exists(path):
            return {}
        # Open and parse the JSON file
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_all_foods(data):
        """
        Saves the entire food dictionary back into the JSON database file.

        Parameters:
            data (dict): The complete foods dictionary to write.
        """
        path = NutritionService._get_db_path()
        # Write formatted JSON data with 4-space indentation for readability
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def get_food(key):
        """
        Finds a single food item by its unique dictionary key.

        Parameters:
            key (str): The unique lookup identifier for the food.

        Returns:
            dict or None: Nutrition info dictionary if found, else None.
        """
        foods = NutritionService.get_all_foods()
        return foods.get(key)

    @staticmethod
    def update_food(original_key, new_key, friendly_name, calories, protein, carbs, fat):
        """
        Updates an existing food entry with new values or a renamed key.

        Parameters:
            original_key (str): The current key of the food item.
            new_key (str): The new/updated key for the food item.
            friendly_name (str): Human-readable name for display.
            calories, protein, carbs, fat: Macro nutrition values.

        Returns:
            tuple: (success: bool, message: str)
        """
        foods = NutritionService.get_all_foods()
        
        # If the key changed, ensure new key doesn't overwrite another existing one
        if original_key != new_key and new_key in foods:
            return False, "A food item with that key already exists."

        # Remove the old key if it changed
        if original_key != new_key and original_key in foods:
            del foods[original_key]
            
        # Store the updated food record
        foods[new_key] = {
            "friendly_name": friendly_name,
            "calories": float(calories),
            "protein": float(protein),
            "carbs": float(carbs),
            "fat": float(fat)
        }
        
        # Save back to file
        NutritionService.save_all_foods(foods)
        return True, "Food updated successfully."

    @staticmethod
    def add_food(key, friendly_name, calories, protein, carbs, fat):
        """
        Adds a new food entry to the nutrition database.

        Parameters:
            key (str): Unique identifier for the new food.
            friendly_name (str): Human-readable name for display.
            calories, protein, carbs, fat: Macro nutrition values.

        Returns:
            tuple: (success: bool, message: str)
        """
        foods = NutritionService.get_all_foods()
        
        # Prevent duplicate keys
        if key in foods:
            return False, "A food item with that key already exists."
            
        # Create new food dictionary
        foods[key] = {
            "friendly_name": friendly_name,
            "calories": float(calories),
            "protein": float(protein),
            "carbs": float(carbs),
            "fat": float(fat)
        }
        
        # Save changes to the JSON file
        NutritionService.save_all_foods(foods)
        return True, "Food added successfully."

    @staticmethod
    def delete_food(key):
        """
        Deletes a food item from the nutrition database by key.

        Parameters:
            key (str): The unique identifier of the food to remove.

        Returns:
            tuple: (success: bool, message: str)
        """
        foods = NutritionService.get_all_foods()
        # Check if the food item exists before deleting
        if key in foods:
            del foods[key]
            NutritionService.save_all_foods(foods)
            return True, "Food deleted successfully."
        return False, "Food not found."
