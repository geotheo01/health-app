"""
AI Financial Advisor Blueprint (Controller Layer)
Thesis Project - Personal Finance Management Application

This file defines the Flask Blueprint for the AI Financial Advisor subsystem, adhering to the
Model-View-Controller (MVC) architectural pattern. It acts as the Controller component,
routing HTTP requests and managing the flow of data between the frontend templates/AJAX calls
and the underlying service/DAO layers.

Responsibilities:
- Render the primary dashboard view for AI recommendations.
- Invoke service logic to handle integration with external LLM services (e.g., Google Gemini API).
- Process asynchronous AJAX requests for generating and force-refreshing recommendations.
- Restrict endpoint access to authenticated users via Flask-Login decorators.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.services.recommendation_service import RecommendationService
from datetime import date

# Instantiating the advisor Blueprint to organize route handlers for this module
advisor_bp = Blueprint('advisor', __name__)

@advisor_bp.route('/advisor')
@login_required
def index():
    """
    Renders the main dashboard page for the AI Financial Advisor interface.

    To ensure responsive performance and avoid unnecessary external API overhead, 
    this view retrieves pre-existing recommendations stored in the database rather 
    than requesting fresh generation from the LLM on every page refresh.

    Returns:
        Rendered HTML template ('ai/advisor.html') populated with recommendation data.
    """
    # Load existing recommendations from DB instantly (no Gemini call) to minimize response latency
    recs = RecommendationService.get_user_recommendations(current_user.id)
    
    # Check whether recommendations have already been generated for today's date
    has_today = len(recs) > 0
    
    # Pass recommendation data and temporal flags to the view layer for dynamic rendering
    return render_template('ai/advisor.html',
                           recommendations=recs,
                           today=date.today(),
                           has_today=has_today)

@advisor_bp.route('/advisor/generate', methods=['POST'])
@login_required
def generate():
    """
    AJAX endpoint: generates new recommendations and returns them as JSON.

    Invokes the business logic layer to generate daily financial insights for the 
    authenticated user, serializes the resulting domain objects, and returns them as JSON.

    Returns:
        JSON response with status payload and serialized recommendation objects, 
        or an HTTP 500 status code on generation failure.
    """
    try:
        # Trigger the service layer to process financial data and retrieve new AI insights
        recs = RecommendationService.generate_daily_recommendations(current_user.id)
        
        # Serialize ORM objects into dictionary format for JSON representation
        data = []
        for r in recs:
            data.append({
                'category':    r.category,
                'message':     r.message,
                'explanation': r.explanation
            })
            
        # Return success status alongside serialized recommendations payload
        return jsonify({'success': True, 'recommendations': data})
    except Exception as e:
        # Catch unexpected exceptions (e.g., API failures or database issues) and report to client
        return jsonify({'success': False, 'error': str(e)}), 500

@advisor_bp.route('/advisor/refresh', methods=['POST'])
@login_required
def refresh():
    """
    Force-refresh endpoint: delete today's recs and regenerate.

    Deletes any recommendation entries already associated with the user for today's date 
    via the DAO layer, then delegates execution to the generate route to rebuild recommendations.

    Returns:
        JSON response produced by the `generate()` route.
    """
    # Local import of DAO class to prevent potential circular dependency issues at the module level
    from app.dao.recommendation_dao import RecommendationDAO
    
    # Remove existing database records for the current user matching today's date
    RecommendationDAO.delete_for_user_and_date(current_user.id, date.today())
    
    # Re-generate fresh recommendations by calling the generate function directly
    return generate()
