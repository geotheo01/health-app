"""
Goals Controller / Blueprint Module

This module serves as the Controller component within the application's Model-View-Controller 
(MVC) architecture for user goal management. It handles incoming HTTP requests related to 
retrieving, creating, and updating personal target metrics (e.g., calories, water, sleep). 
Business logic and persistence operations are delegated to the GoalService layer to maintain 
a clean separation of concerns.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.goal_service import GoalService

# Instantiate the Flask Blueprint for goal-related routes and views
goals_bp = Blueprint('goals', __name__)

@goals_bp.route('/goals')
@login_required
def view():
    """
    Display the user's current goal dashboard.

    Requires user authentication. Fetches the goal records for the currently 
    logged-in user from the service layer and passes them to the rendering engine.

    Returns:
        str: Rendered HTML template ('goals/view.html') populated with goal data.
    """
    # Fetch the authenticated user's target goals via the service layer
    goal = GoalService.get_user_goal(current_user.id)
    
    # Render the goal viewing template with the retrieved data
    return render_template('goals/view.html', goal=goal)

@goals_bp.route('/goals/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """
    Handle the viewing and updating of user health and fitness goals.

    For GET requests: Retrieves current goal values to populate the edit form.
    For POST requests: Parses form data with explicit type conversion, passes data 
    to the service layer for processing/validation, and returns feedback to the user.

    Returns:
        str | Response: Redirects to view page on successful POST, or renders 
                        the edit form template on GET / validation failure.
    """
    # Query existing goal settings to pre-populate the edit form fields
    goal = GoalService.get_user_goal(current_user.id)
    
    # Handle submission of updated goal values
    if request.method == 'POST':
        # Safely extract and type-cast form inputs into a structured payload
        data = {
            'daily_calorie_goal': request.form.get('daily_calorie_goal', type=int),
            'daily_water_goal': request.form.get('daily_water_goal', type=float),
            'daily_sleep_goal': request.form.get('daily_sleep_goal', type=float),
            'weekly_exercise_goal': request.form.get('weekly_exercise_goal', type=int),
            'target_weight': request.form.get('target_weight', type=float)
        }
        
        # Delegate record creation or update to the GoalService layer
        success, result = GoalService.update_or_create_goal(current_user.id, data)
        
        if success:
            # Provide feedback and navigate back to the main goals dashboard
            flash('Goals updated successfully!', 'success')
            return redirect(url_for('goals.view'))
        else:
            # Display error or validation message returned by the service
            flash(result, 'danger')
    
    # Render the edit form (serves GET request or re-renders on failed POST attempt)
    return render_template('goals/edit.html', goal=goal)
