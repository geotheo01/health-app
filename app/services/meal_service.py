"""
Meal Service Module.

This service handles all operations related to meals in the health application:
- Validating meal items and macro nutrition values (calories, protein, carbs, fat)
- Calculating total calories and macronutrients for multi-item meals
- Handling user photo uploads for meals securely
- Creating, updating, and deleting meal logs in the database
- Integrating with the AI meal image analysis service
- Saving and retrieving favorite/preset meals for quick re-use
"""

from app.dao.meal_dao import MealDAO
from app.models.meal import Meal, MealItem
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

# Set of permitted image file extensions for uploaded meal photos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    """
    Check if an uploaded file has one of the allowed image extensions.
    
    Parameters:
        filename (str): Name of the file being uploaded.
        
    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class MealService:
    """
    MealService encapsulates the business logic for managing meals,
    handling food item validation, totals calculation, image storage,
    and AI-assisted meal logging.
    """

    @staticmethod
    def validate_item(item_data):
        """
        Validate nutritional numbers for an individual food item.
        Ensures calories and macronutrients are non-negative numbers.

        Parameters:
            item_data (dict): Dictionary containing nutrition fields (calories, protein, carbs, fat).

        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Convert values to floats safely, defaulting to 0 if missing or None
        calories = float(item_data.get('calories', 0) or 0)
        protein = float(item_data.get('protein', 0) or 0)
        carbs = float(item_data.get('carbs', 0) or 0)
        fat = float(item_data.get('fat', 0) or 0)
        
        # Make sure no nutrition values are negative
        if any(val < 0 for val in [calories, protein, carbs, fat]):
            return False, "Calories and macros cannot be negative."
        return True, None

    @staticmethod
    def calculate_totals(items_data):
        """
        Calculate the sum of calories and macronutrients across all food items in a meal.

        Parameters:
            items_data (list): List of dictionaries, where each represents a food item.

        Returns:
            tuple: (total_calories, total_protein, total_carbs, total_fat)
        """
        # Sum up each nutrient across all items
        total_calories = sum(float(item.get('calories', 0) or 0) for item in items_data)
        total_protein = sum(float(item.get('protein', 0) or 0) for item in items_data)
        total_carbs = sum(float(item.get('carbs', 0) or 0) for item in items_data)
        total_fat = sum(float(item.get('fat', 0) or 0) for item in items_data)
        return total_calories, total_protein, total_carbs, total_fat

    @staticmethod
    def handle_image_upload(image_file, static_folder):
        """
        Validates and saves an uploaded meal image to the static uploads directory.

        Parameters:
            image_file (FileStorage): The uploaded file object from the form.
            static_folder (str): The path to the application's static assets directory.

        Returns:
            tuple: (success: bool, file_path_or_error: str or None)
        """
        # If no file was provided or filename is empty, nothing to upload
        if not image_file or not image_file.filename:
            return True, None
            
        # Verify the file extension against allowed types
        if not allowed_file(image_file.filename):
            return False, "Invalid file type. Only JPG, PNG and WEBP are allowed."
            
        # Sanitize filename and generate a unique UUID name to avoid collisions
        filename = secure_filename(image_file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Ensure the target directory exists on disk
        upload_dir = os.path.join(static_folder, 'uploads', 'meals')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file to disk
        file_path = os.path.join(upload_dir, unique_filename)
        image_file.save(file_path)
        
        # Return relative URL path stored in the database
        return True, f"uploads/meals/{unique_filename}"

    @staticmethod
    def create_meal(user_id, meal_data, items_data, image_file=None, static_folder=None):
        """
        Creates a new meal along with its associated food items.

        Parameters:
            user_id (int): ID of the user logging the meal.
            meal_data (dict): Metadata about the meal (meal_date, meal_type, title, etc.).
            items_data (list): List of dictionaries containing individual food items.
            image_file (FileStorage, optional): Uploaded meal photo.
            static_folder (str, optional): Static folder path for saving photos.

        Returns:
            tuple: (success: bool, result: Meal object or error message string)
        """
        # Parse the meal date string into a date object
        try:
            meal_date = datetime.strptime(meal_data.get('meal_date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return False, "Invalid date format."

        # Validate each individual food item entered
        for item in items_data:
            if not item.get('food_name'):
                continue
            is_valid, msg = MealService.validate_item(item)
            if not is_valid:
                return False, msg
                
        # Handle image upload if a photo was attached
        image_path = None
        if image_file and static_folder:
            success, result = MealService.handle_image_upload(image_file, static_folder)
            if not success:
                return False, result
            image_path = result

        # Calculate macro totals from all items
        t_cal, t_pro, t_carb, t_fat = MealService.calculate_totals(items_data)

        # Build the parent Meal record
        meal = Meal(
            user_id=user_id,
            meal_date=meal_date,
            meal_type=meal_data.get('meal_type'),
            title=meal_data.get('title'),
            total_calories=t_cal,
            total_protein=t_pro,
            total_carbs=t_carb,
            total_fat=t_fat,
            image_path=image_path
        )

        # Build MealItem child records and attach them to the meal
        for item_data in items_data:
            if not item_data.get('food_name'):
                continue
            item = MealItem(
                food_name=item_data.get('food_name'),
                quantity=item_data.get('quantity'),
                calories=float(item_data.get('calories', 0) or 0),
                protein=float(item_data.get('protein', 0) or 0),
                carbs=float(item_data.get('carbs', 0) or 0),
                fat=float(item_data.get('fat', 0) or 0)
            )
            meal.items.append(item)

        # Save meal and its items to database
        saved_meal = MealDAO.save(meal)
        
        # If the user checked "Save as favorite", also save a favorite meal template
        if meal_data.get('save_as_favorite') == 'true' or meal_data.get('save_as_favorite') is True:
            MealService.save_as_favorite(user_id, meal_data, items_data)

        return True, saved_meal

    @staticmethod
    def update_meal(meal_id, user_id, meal_data, items_data, image_file=None, static_folder=None):
        """
        Updates an existing meal and replaces its item details.

        Parameters:
            meal_id (int): ID of the meal being updated.
            user_id (int): ID of the user (to verify ownership).
            meal_data (dict): Updated meal fields (date, type, title).
            items_data (list): Updated list of food items.
            image_file (FileStorage, optional): New photo upload if replaced.
            static_folder (str, optional): Static folder path.

        Returns:
            tuple: (success: bool, result: Meal object or error message string)
        """
        # Fetch the meal and verify it belongs to this user
        meal = MealDAO.get_by_id(meal_id)
        if not meal or meal.user_id != user_id:
            return False, "Meal not found or access denied."

        # Parse date
        try:
            meal.meal_date = datetime.strptime(meal_data.get('meal_date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return False, "Invalid date format."

        # Update basic meal attributes
        meal.meal_type = meal_data.get('meal_type')
        meal.title = meal_data.get('title')

        # Validate all provided items
        for item in items_data:
            if not item.get('food_name'):
                continue
            is_valid, msg = MealService.validate_item(item)
            if not is_valid:
                return False, msg

        # Handle new image upload if provided
        if image_file and static_folder:
            success, result = MealService.handle_image_upload(image_file, static_folder)
            if not success:
                return False, result
            if result:
                meal.image_path = result

        # Clear existing items to replace with updated list
        meal.items = [] # clear existing items

        # Recalculate totals
        t_cal, t_pro, t_carb, t_fat = MealService.calculate_totals(items_data)
        meal.total_calories = t_cal
        meal.total_protein = t_pro
        meal.total_carbs = t_carb
        meal.total_fat = t_fat

        # Append new items to the meal
        for item_data in items_data:
            if not item_data.get('food_name'):
                continue
            item = MealItem(
                food_name=item_data.get('food_name'),
                quantity=item_data.get('quantity'),
                calories=float(item_data.get('calories', 0) or 0),
                protein=float(item_data.get('protein', 0) or 0),
                carbs=float(item_data.get('carbs', 0) or 0),
                fat=float(item_data.get('fat', 0) or 0)
            )
            meal.items.append(item)

        # Save and return updated meal
        return True, MealDAO.save(meal)

    @staticmethod
    def apply_ai_analysis(meal_id, user_id):
        """
        Uses an AI image analysis service to detect the meal and estimate nutrition from its photo.

        Parameters:
            meal_id (int): ID of the meal to analyze.
            user_id (int): ID of the requesting user.

        Returns:
            tuple: (success: bool, message: str)
        """
        # Lazy import to avoid circular dependencies
        from app.services.image_analysis_service import ImageAnalysisService
        
        # Verify meal exists and belongs to the user
        meal = MealDAO.get_by_id(meal_id)
        if not meal or meal.user_id != user_id:
            return False, "Meal not found or access denied."
            
        # Ensure the meal actually has a photo attached
        if not meal.image_path:
            return False, "This meal does not have an image to analyze."
            
        # Call the image analysis AI service
        success, analysis = ImageAnalysisService.analyze_meal_image(meal.image_path)
        if not success:
            return False, analysis
            
        # Replace items with AI-detected food item
        meal.items = []
        item = MealItem(
            food_name=analysis['detected_food_name'],
            quantity='1 serving',
            calories=analysis['estimated_calories'],
            protein=analysis['protein'],
            carbs=analysis['carbs'],
            fat=analysis['fat']
        )
        meal.items.append(item)
        
        # Update meal nutrition and AI confidence score
        meal.total_calories = analysis['estimated_calories']
        meal.total_protein = analysis['protein']
        meal.total_carbs = analysis['carbs']
        meal.total_fat = analysis['fat']
        meal.ai_confidence = analysis['confidence']
        
        # Save changes to the database
        MealDAO.save(meal)
        return True, "Meal updated with AI analysis."

    @staticmethod
    def get_user_favorites(user_id):
        """
        Fetches all saved favorite meal templates for a user.

        Parameters:
            user_id (int): The user's ID.

        Returns:
            list: List of FavoriteMeal objects.
        """
        from app.dao.favorite_meal_dao import FavoriteMealDAO
        return FavoriteMealDAO.get_user_favorites(user_id)

    @staticmethod
    def save_as_favorite(user_id, meal_data, items_data):
        """
        Saves a meal configuration as a reusable favorite template.

        Parameters:
            user_id (int): The user's ID.
            meal_data (dict): Meal metadata (title, meal_type).
            items_data (list): List of food items in the meal.

        Returns:
            FavoriteMeal: The saved favorite meal record.
        """
        from app.dao.favorite_meal_dao import FavoriteMealDAO
        from app.models.favorite_meal import FavoriteMeal
        import json
        
        # Calculate total nutrients for the favorite template
        t_cal, t_pro, t_carb, t_fat = MealService.calculate_totals(items_data)
        
        # Create and persist the FavoriteMeal entity
        favorite = FavoriteMeal(
            user_id=user_id,
            title=meal_data.get('title', 'Quick Meal'),
            meal_type=meal_data.get('meal_type', 'snack'),
            total_calories=t_cal,
            total_protein=t_pro,
            total_carbs=t_carb,
            total_fat=t_fat,
            items_json=json.dumps(items_data)
        )
        return FavoriteMealDAO.save(favorite)

    @staticmethod
    def delete_meal(meal_id, user_id):
        """
        Deletes a meal from the database after verifying user ownership.

        Parameters:
            meal_id (int): ID of the meal to delete.
            user_id (int): ID of the user requesting deletion.

        Returns:
            tuple: (success: bool, message: str)
        """
        meal = MealDAO.get_by_id(meal_id)
        if not meal or meal.user_id != user_id:
            return False, "Meal not found or access denied."
        # Remove meal from the database
        MealDAO.delete(meal)
        return True, "Meal deleted successfully."
