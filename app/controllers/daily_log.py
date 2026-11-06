"""
Daily Log Controller Module

This module serves as the Controller component within the Model-View-Controller (MVC) 
architecture for the application's daily logging subsystem. It relies on Flask Blueprints 
to group endpoints associated with creating, reading, updating, and deleting (CRUD) 
user habit and health tracking logs.

Responsibilities:
- Route HTTP requests to proper handlers.
- Enforce authentication via Flask-Login (@login_required).
- Extract and type-cast request form payload data.
- Interact with the Service layer (DailyLogService) for business logic and validation.
- Interact with the Data Access Object (DailyLogDAO) for straightforward queries.
- Render appropriate HTML view templates or execute HTTP redirects with flash alerts.

Author: CS Undergraduate Thesis Student
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.daily_log_service import DailyLogService
from app.dao.daily_log_dao import DailyLogDAO
from datetime import date

# Initialize Blueprint for logs-related routes
logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs')
@login_required
def list_logs():
    """
    Display a listed view of all daily logs created by the currently logged-in user.

    Returns:
        Response: Rendered template showing user's historic logs.
    """
    # Fetch all log records for the authenticated user directly from the DAO layer
    logs = DailyLogDAO.get_user_logs(current_user.id)
    return render_template('logs/list.html', logs=logs)

@logs_bp.route('/logs/new', methods=['GET', 'POST'])
@login_required
def create():
    """
    Handle rendering the log creation form (GET) and processing new log creation (POST).

    Returns:
        Response: Redirect to list view on successful creation, or rendered form on GET / error.
    """
    if request.method == 'POST':
        # Extract and cast incoming HTTP POST form parameters to appropriate Python data types
        data = {
            'log_date': request.form.get('log_date'),
            'sleep_hours': request.form.get('sleep_hours', type=float),
            'water_liters': request.form.get('water_liters', type=float),
            'exercise_minutes': request.form.get('exercise_minutes', type=int),
            'mood_score': request.form.get('mood_score', type=int),
            'weight_kg': request.form.get('weight_kg', type=float),
            'notes': request.form.get('notes')
        }
        
        # Delegate business logic and persistence validation to the service layer
        success, result = DailyLogService.create_log(current_user.id, data)
        if success:
            flash('Log created successfully!', 'success')
            return redirect(url_for('logs.list_logs'))
        else:
            # Display error message returned from the service layer validation
            flash(result, 'danger')
    
    # Render empty log entry form for GET requests, providing today's date as a default baseline
    return render_template('logs/form.html', today=date.today().isoformat(), log=None)

@logs_bp.route('/logs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Handle updating an existing daily log entry identified by its primary key.

    Args:
        id (int): The unique identifier of the daily log to be edited.

    Returns:
        Response: Redirect back to log list after modification or authorization failure;
                  renders edit form template otherwise.
    """
    # Query database for the target log entry
    log = DailyLogDAO.get_by_id(id)
    
    # Enforce access control ownership check to prevent unauthorized user access
    if not log or log.user_id != current_user.id:
        flash('Log not found.', 'danger')
        return redirect(url_for('logs.list_logs'))

    if request.method == 'POST':
        # Collect updated form parameters with correct type casting
        data = {
            'sleep_hours': request.form.get('sleep_hours', type=float),
            'water_liters': request.form.get('water_liters', type=float),
            'exercise_minutes': request.form.get('exercise_minutes', type=int),
            'mood_score': request.form.get('mood_score', type=int),
            'weight_kg': request.form.get('weight_kg', type=float),
            'notes': request.form.get('notes')
        }
        
        # Pass update dictionary to the service layer for validation and database commit
        success, result = DailyLogService.update_log(id, current_user.id, data)
        if success:
            flash('Log updated successfully!', 'success')
            return redirect(url_for('logs.list_logs'))
        else:
            flash(result, 'danger')

    # Render form pre-populated with existing log data for GET requests
    return render_template('logs/form.html', log=log)

@logs_bp.route('/logs/<int:id>/delete')
@login_required
def delete(id):
    """
    Delete a specific daily log entry belonging to the logged-in user.

    Args:
        id (int): The primary key ID of the log record to remove.

    Returns:
        Response: Redirect to the list view accompanied by a flash feedback message.
    """
    # Trigger deletion via service layer to guarantee user ownership validation
    success, message = DailyLogService.delete_log(id, current_user.id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('logs.list_logs'))
