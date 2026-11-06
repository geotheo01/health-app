"""
Meals Blueprint Controller Module.

This file serves as the Controller component within the Model-View-Controller (MVC)
architecture of the application. It handles incoming HTTP requests related to meal 
tracking, recipe favorites, AI-driven nutritional analysis, and meal logging. 

To maintain clean architecture and separation of concerns:
- Data retrieval and database operations are delegated to Data Access Objects (DAOs).
- Core business logic, validation, and AI processing are handled by the Service layer.
- View rendering and response formatting are passed off to Jinja2 HTML templates.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.services.meal_service import MealService
from app.dao.meal_dao import MealDAO
from datetime import date

# Initialize Flask Blueprint for meal-related routing
meals_bp = Blueprint('meals', __name__)

@meals_bp.route('/meals')
@login_required
def list_meals():
    """
    Display a list of all historical meals logged by the currently authenticated user.
    """
    # Query database via DAO for meals associated with the logged-in user
    meals = MealDAO.get_user_meals(current_user.id)
    return render_template('meals/list.html', meals=meals)

@meals_bp.route('/meals/new', methods=['GET', 'POST'])
@login_required
def create():
    """
    Handle creation of new meal entries.
    
    Processes both GET requests (displaying the creation form along with user favorites)
    and POST requests (parsing form input, processing uploads, and persisting data).
    """
    if request.method == 'POST':
        # Extract general meal metadata from submitted form data
        meal_data = {
            'meal_date': request.form.get('meal_date'),
            'meal_type': request.form.get('meal_type'),
            'title': request.form.get('title'),
            'save_as_favorite': request.form.get('save_as_favorite') == 'on'
        }
        
        # Retrieve optional uploaded meal image file
        image_file = request.files.get('meal_image')
        
        # Parse parallel arrays from dynamic form fields for individual food items
        food_names = request.form.getlist('food_name[]')
        quantities = request.form.getlist('quantity[]')
        calories = request.form.getlist('calories[]')
        proteins = request.form.getlist('protein[]')
        carbs = request.form.getlist('carbs[]')
        fats = request.form.getlist('fat[]')

        # Structure individual item data with defensive fallback defaults for missing values
        items_data = []
        for i in range(len(food_names)):
            if food_names[i].strip():  # Skip empty or whitespace-only item rows
                items_data.append({
                    'food_name': food_names[i],
                    'quantity': quantities[i] if i < len(quantities) else '',
                    'calories': calories[i] if i < len(calories) else 0,
                    'protein': proteins[i] if i < len(proteins) else 0,
                    'carbs': carbs[i] if i < len(carbs) else 0,
                    'fat': fats[i] if i < len(fats) else 0
                })

        # Delegate business logic and storage handling to the service layer
        success, result = MealService.create_meal(current_user.id, meal_data, items_data, image_file, current_app.static_folder)
        if success:
            flash('Meal created successfully!', 'success')
            return redirect(url_for('meals.list_meals'))
        else:
            flash(result, 'danger')
            
    # GET request handler: fetch saved favorites to assist quick filling in the form UI
    favorites = MealService.get_user_favorites(current_user.id)
    return render_template('meals/form.html', today=date.today().isoformat(), meal=None, favorites=favorites)

@meals_bp.route('/meals/<int:id>')
@login_required
def view(id):
    """
    View detailed information for a specific meal entry.
    """
    meal = MealDAO.get_by_id(id)
    
    # Enforce strict authorization: users can only view their own meal records
    if not meal or meal.user_id != current_user.id:
        flash('Meal not found.', 'danger')
        return redirect(url_for('meals.list_meals'))
        
    return render_template('meals/view.html', meal=meal)

@meals_bp.route('/meals/<int:id>/analyze', methods=['POST'])
@login_required
def analyze_image(id):
    """
    Trigger automated AI analysis on an uploaded meal image to extract nutritional insights.
    """
    # Delegate computer vision / multimodal AI analysis to the service layer
    success, message = MealService.apply_ai_analysis(id, current_user.id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('meals.view', id=id))

@meals_bp.route('/meals/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit an existing meal entry and update its associated food items and image.
    """
    # Fetch existing record and perform ownership authorization check
    meal = MealDAO.get_by_id(id)
    if not meal or meal.user_id != current_user.id:
        flash('Meal not found.', 'danger')
        return redirect(url_for('meals.list_meals'))

    if request.method == 'POST':
        # Extract updated metadata parameters
        meal_data = {
            'meal_date': request.form.get('meal_date'),
            'meal_type': request.form.get('meal_type'),
            'title': request.form.get('title')
        }
        
        image_file = request.files.get('meal_image')
        
        # Extract parallel lists submitted from dynamic JavaScript form inputs
        food_names = request.form.getlist('food_name[]')
        quantities = request.form.getlist('quantity[]')
        calories = request.form.getlist('calories[]')
        proteins = request.form.getlist('protein[]')
        carbs = request.form.getlist('carbs[]')
        fats = request.form.getlist('fat[]')

        # Reconstruct updated list of structured item dictionaries
        items_data = []
        for i in range(len(food_names)):
            if food_names[i].strip():
                items_data.append({
                    'food_name': food_names[i],
                    'quantity': quantities[i] if i < len(quantities) else '',
                    'calories': calories[i] if i < len(calories) else 0,
                    'protein': proteins[i] if i < len(proteins) else 0,
                    'carbs': carbs[i] if i < len(carbs) else 0,
                    'fat': fats[i] if i < len(fats) else 0
                })

        # Process updates through business logic layer
        success, result = MealService.update_meal(id, current_user.id, meal_data, items_data, image_file, current_app.static_folder)
        if success:
            flash('Meal updated successfully!', 'success')
            return redirect(url_for('meals.view', id=meal.id))
        else:
            flash(result, 'danger')

    favorites = MealService.get_user_favorites(current_user.id)
    return render_template('meals/form.html', meal=meal, favorites=favorites)

@meals_bp.route('/meals/<int:id>/delete')
@login_required
def delete(id):
    """
    Delete a specific meal entry and its associated database records.
    """
    success, message = MealService.delete_meal(id, current_user.id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('meals.list_meals'))

@meals_bp.route('/meals/favorites')
@login_required
def favorite_meals_list():
    """
    Display user's saved favorite recipes and calculate a dynamic AI recipe recommendation
    based on the user's remaining daily target intake.
    """
    # Lazy import to avoid circular dependency issues at dynamic initialization
    from app.services.dashboard_service import DashboardService
    favorites = MealService.get_user_favorites(current_user.id)
    
    # Calculate daily remaining macro targets for AI Suggestions!
    dash_data = DashboardService.get_dashboard_data(current_user.id)
    remaining_calories = max(0, (current_user.goal.daily_calorie_goal if current_user.goal else 2000) - dash_data['total_calories'])
    
    # Simple, highly-intelligent AI Recipe Matcher that suggests the best favorite meal based on remaining macros!
    # Nearest-neighbor matching algorithm evaluating absolute distance to remaining target calories
    suggested_recipe = None
    if favorites:
        best_diff = float('inf')
        for fav in favorites:
            if fav.total_calories > 0:
                diff = abs(fav.total_calories - remaining_calories)
                if diff < best_diff:
                    best_diff = diff
                    suggested_recipe = fav
                    
    return render_template('meals/favorites.html', favorites=favorites, suggested_recipe=suggested_recipe, remaining_calories=remaining_calories)

@meals_bp.route('/meals/favorites/log/<int:id>')
@login_required
def log_favorite(id):
    """
    Instantiate and log a new meal entry for today directly from a saved favorite recipe template.
    """
    from app.dao.favorite_meal_dao import FavoriteMealDAO
    import json
    from datetime import date
    
    # Verify recipe existence and ownership
    favorite = FavoriteMealDAO.get_by_id(id)
    if not favorite or favorite.user_id != current_user.id:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('meals.favorite_meals_list'))
        
    # Reconstruct items list from JSON template stored in database
    items_data = []
    if favorite.items_json:
        try:
            items_data = json.loads(favorite.items_json)
        except Exception:
            pass
            
    # Prepare standard meal payload for the current system date
    meal_data = {
        'meal_date': date.today().isoformat(),
        'meal_type': favorite.meal_type,
        'title': favorite.title
    }
    
    # Delegate creation to core service
    success, result = MealService.create_meal(current_user.id, meal_data, items_data)
    if success:
        flash('Recipe Logged Successfully!', 'success')
    else:
        flash(result, 'danger')
        
    return redirect(url_for('meals.list_meals'))

@meals_bp.route('/meals/favorites/delete/<int:id>')
@login_required
def delete_favorite(id):
    """
    Remove a saved recipe from the user's favorites list.
    """
    from app.dao.favorite_meal_dao import FavoriteMealDAO
    from app import db
    
    favorite = FavoriteMealDAO.get_by_id(id)
    if not favorite or favorite.user_id != current_user.id:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('meals.favorite_meals_list'))
        
    # Execute database deletion transaction
    db.session.delete(favorite)
    db.session.commit()
    flash('Recipe deleted successfully.', 'success')
    return redirect(url_for('meals.favorite_meals_list'))
