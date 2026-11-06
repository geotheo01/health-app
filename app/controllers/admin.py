"""
Admin Controller Module (Blueprint)

This module serves as the Controller component within the Model-View-Controller (MVC) 
architectural pattern for the administration subsystem. It manages HTTP request routing, 
enforces authentication and authorization controls (RBAC), interacts with the Service 
and Data Access Object (DAO) layers for business logic execution, and renders the appropriate 
Jinja2 view templates for display.

Author: Computer Science Undergraduate Student
Project: Final Year Thesis Project
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.decorators import admin_required
from app.services.admin_service import AdminService
from app.services.admin_stats_service import AdminStatsService
from app.dao.user_dao import UserDAO

# Initialize Flask Blueprint for administrative routing scope
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    """
    Render the central administrative dashboard.
    
    Gathers high-level system analytics and aggregate metrics to provide
    administrators with an overview of system performance and activity.
    
    Returns:
        Response: Rendered administrative dashboard HTML template.
    """
    # Fetch aggregated statistical data from the dedicated stats service
    stats = AdminStatsService.get_system_stats()
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users_list():
    """
    Display the user management page listing all registered application users.
    
    Returns:
        Response: Rendered template containing the list of users.
    """
    # Retrieve complete list of registered users via service layer abstraction
    users = AdminService.get_all_users()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/<int:id>/toggle-active')
@login_required
@admin_required
def toggle_active(id):
    """
    Toggle a user's account status between active and suspended states.
    
    Args:
        id (int): Unique identifier of the target user.
        
    Returns:
        Response: Redirect to the user management list with user feedback.
    """
    # Delegate account state modification to the service layer
    if AdminService.toggle_user_active(id):
        flash('User status updated.', 'success')
    else:
        flash('User not found.', 'danger')
    # Standard Post/Redirect/Get pattern to prevent re-submission issues
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/admin/users/<int:id>/change-role')
@login_required
@admin_required
def change_role(id):
    """
    Update the authorization role assigned to a user account.
    
    Args:
        id (int): Unique identifier of the target user.
        
    Returns:
        Response: Redirect to user management page with success/failure notification.
    """
    # Extract requested target role from HTTP GET URL parameters
    new_role = request.args.get('role')
    
    # Attempt role modification via service layer
    if AdminService.change_user_role(id, new_role):
        flash(f'User role changed to {new_role}.', 'success')
    else:
        flash('Operation failed.', 'danger')
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/admin/users/<int:id>/delete')
@login_required
@admin_required
def delete_user(id):
    """
    Safely remove a user account from the system database.
    
    Args:
        id (int): Unique identifier of the user to be removed.
        
    Returns:
        Response: Redirect to user list with status flash message.
    """
    # Service call includes current user ID to prevent self-deletion security issues
    success, message = AdminService.delete_user(id, current_user.id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """
    Handle user profile edit form rendering (GET) and data persistence (POST).
    
    Args:
        id (int): Unique identifier of the user account being modified.
        
    Returns:
        Response: HTML form template (GET/Error) or redirect to user list (Success).
    """
    # Retrieve domain entity directly via Data Access Object (DAO) pattern
    user = UserDAO.get_by_id(id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users_list'))
        
    # Process form payload upon HTTP POST submission
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Execute business logic for updating account parameters
        success, message = AdminService.update_user(id, email, username, full_name, password)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.users_list'))
        else:
            flash(message, 'danger')
            
    # Render user edit form on GET request or failed form validation
    return render_template('admin/edit_user.html', user=user)

# --- Nutrition Database Routes ---

from app.services.nutrition_service import NutritionService

@admin_bp.route('/admin/foods')
@login_required
@admin_required
def foods_list():
    """
    Display complete list of nutritional items stored in the catalog.
    
    Returns:
        Response: Rendered HTML page with list of nutritional entries.
    """
    # Fetch all registered food items from domain service layer
    foods = NutritionService.get_all_foods()
    return render_template('admin/foods.html', foods=foods)

@admin_bp.route('/admin/foods/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_food():
    """
    Provide interface and process form submission for registering a new food item.
    
    Returns:
        Response: Rendered creation form or redirect to catalog on success.
    """
    # Handle incoming creation payload
    if request.method == 'POST':
        key = request.form.get('key')
        friendly_name = request.form.get('friendly_name')
        calories = request.form.get('calories')
        protein = request.form.get('protein')
        carbs = request.form.get('carbs')
        fat = request.form.get('fat')
        
        # Delegate record validation and insertion to service layer
        success, message = NutritionService.add_food(key, friendly_name, calories, protein, carbs, fat)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.foods_list'))
        else:
            flash(message, 'danger')
            
    # Render blank creation form for GET requests
    return render_template('admin/edit_food.html', food=None, food_key="")

@admin_bp.route('/admin/foods/<key>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_food(key):
    """
    Manage existing nutritional entity modification specified by its primary key string.
    
    Args:
        key (str): Primary key string identifier of the nutritional item.
        
    Returns:
        Response: Rendered edit form template or redirect to food inventory.
    """
    # Verify entity presence prior to allowing modification operations
    food = NutritionService.get_food(key)
    if not food:
        flash('Food not found.', 'danger')
        return redirect(url_for('admin.foods_list'))
        
    # Extract updated attributes from POST request payload
    if request.method == 'POST':
        new_key = request.form.get('key')
        friendly_name = request.form.get('friendly_name')
        calories = request.form.get('calories')
        protein = request.form.get('protein')
        carbs = request.form.get('carbs')
        fat = request.form.get('fat')
        
        # Execute atomic update transaction within service layer
        success, message = NutritionService.update_food(key, new_key, friendly_name, calories, protein, carbs, fat)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.foods_list'))
        else:
            flash(message, 'danger')
            
    # Populate edit interface with current item values
    return render_template('admin/edit_food.html', food=food, food_key=key)

@admin_bp.route('/admin/foods/<key>/delete')
@login_required
@admin_required
def delete_food(key):
    """
    Delete a specific food entry from the nutrition database.
    
    Args:
        key (str): Key identifier of the food item to be removed.
        
    Returns:
        Response: Redirect to food catalog with status result message.
    """
    # Delegate entity removal to nutrition management service
    success, message = NutritionService.delete_food(key)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin.foods_list'))
