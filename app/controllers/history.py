"""
History Controller / Blueprint Module

This module serves as the Controller component within the Model-View-Controller (MVC) 
architecture for managing user activity history and report generation functionality.
It defines routes under the 'history' blueprint, delegating database queries and 
business logic processing to the underlying service layer (HistoryService and DashboardService).
"""

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.services.history_service import HistoryService

# Instantiate the Flask Blueprint for history-related endpoints
history_bp = Blueprint('history', __name__)

@history_bp.route('/history')
@login_required
def index():
    """
    Render the main historical logs view for the authenticated user.

    Extracts optional date filtering parameters from request parameters, retrieves the 
    user's logged metrics via the HistoryService, and renders the main history interface.

    Returns:
        str: HTML template rendering the user's historical log entries.
    """
    # Extract query parameters for flexible timeframe filtering (defaulting to 7 days)
    date_range = request.args.get('range', '7days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Fetch processed history logs for the current user from the service layer
    data = HistoryService.get_history_data(current_user.id, date_range, start_date, end_date)
    
    # Render the presentation layer with fetched historical metrics
    return render_template('history/index.html', data=data, current_range=date_range)

@history_bp.route('/history/report')
@login_required
def view_report():
    """
    Generate and display a detailed summary report based on user activity history.

    Computes statistical averages (calories, sleep, water consumption, exercise) across 
    the selected date range and aggregates dynamic dashboard metadata for print or export.

    Returns:
        str: HTML template rendering the formatted user activity report.
    """
    # Deferred local import to prevent potential circular import dependencies
    from app.services.dashboard_service import DashboardService
    
    # Retrieve filtering options from query string
    date_range = request.args.get('range', '7days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Query service layer for detailed history logs and overarching dashboard data
    data = HistoryService.get_history_data(current_user.id, date_range, start_date, end_date)
    dash_data = DashboardService.get_dashboard_data(current_user.id)
    
    # Calculate aggregate summary statistics across historical records
    history_list = data['history']
    total_days = len(history_list)
    
    # Compute mean values for key health metrics, enforcing max(1, total_days) to avoid DivisionByZero exceptions
    avg_calories = sum(day['total_calories'] for day in history_list) / max(1, total_days)
    avg_sleep = sum(day['sleep'] for day in history_list) / max(1, total_days)
    avg_water = sum(day['water'] for day in history_list) / max(1, total_days)
    avg_exercise = sum(day['exercise'] for day in history_list) / max(1, total_days)
    
    # Generate timestamp string indicating when this static snapshot/report was created
    from datetime import datetime
    generation_time = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # Pass calculated analytical aggregates and report metadata to the template view
    return render_template(
        'history/report.html',
        user=current_user,
        data=data,
        dash_data=dash_data,
        avg_calories=avg_calories,
        avg_sleep=avg_sleep,
        avg_water=avg_water,
        avg_exercise=avg_exercise,
        generation_time=generation_time,
        current_range=date_range
    )
