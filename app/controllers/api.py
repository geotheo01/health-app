"""
API Controller Blueprint for the Health and Fitness Tracking Application.

This module acts as part of the Controller layer in our Model-View-Controller (MVC) 
architecture. It exposes RESTful API endpoints for asynchronous client interactions 
(e.g., AJAX/Fetch requests), enabling real-time features such as logging water intake, 
aggregating historical data for frontend charting, and handling uploaded meal photos 
for computer vision analysis. 

Business logic and database persistence are abstracted away into dedicated Service 
modules (DailyLogService, HistoryService, ImageAnalysisService) to preserve modularity 
and clean architectural separation.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.history_service import HistoryService
from app.services.daily_log_service import DailyLogService

# Initialize the API blueprint for endpoint routing
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/logs/water/increment', methods=['POST'])
@login_required
def increment_water():
    """
    Increments the current user's water consumption total for the day.

    Reads the requested volume increment from the JSON payload (defaulting to 0.25L if unprovided),
    invokes the service layer to update the record, and returns the updated total.

    Returns:
        JSON response indicating operation success and the updated total water volume.
    """
    # Extract custom amount from JSON body or default to a standard 0.25L glass size
    amount = request.json.get('amount', 0.25)
    
    # Delegate database update to service layer
    success, log = DailyLogService.increment_water(current_user.id, amount)
    
    if success:
        return jsonify({
            'success': True, 
            'new_total': round(log.water_liters, 2),
            'message': f'Added {amount}L of water!'
        })
    return jsonify({'success': False, 'error': 'Failed to update water'}), 500

@api_bp.route('/api/charts/<string:metric>')
@login_required
def chart_data(metric):
    """
    Retrieves time-series data for a specific metric over a specified date range.

    Supported metrics: 'calories', 'water', 'sleep', 'exercise', 'weight'.
    Transforms historical log entries into separate label (dates) and value (data points) 
    lists suitable for rendering frontend charts (e.g., Chart.js).

    Args:
        metric (str): The requested health/lifestyle metric name.

    Returns:
        JSON response containing formatted labels and corresponding data arrays.
    """
    # Validate requested metric against allowed list
    if metric not in ['calories', 'water', 'sleep', 'exercise', 'weight']:
        return jsonify({'error': 'Invalid metric'}), 400

    # Extract date filter options from query string parameters
    date_range = request.args.get('range', '7days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Fetch aggregated daily history entries for the authenticated user
    data = HistoryService.get_history_data(current_user.id, date_range, start_date, end_date)
    history = data['history']
    
    # Sort ascending for charts to ensure chronological left-to-right rendering
    history.sort(key=lambda x: x['date'])
    
    # Format dates into human-readable string representations for the X-axis labels
    labels = [day['date'].strftime('%b %d') for day in history]
    
    # Extract matching numeric values array based on requested metric
    if metric == 'calories':
        values = [day['total_calories'] for day in history]
    elif metric == 'water':
        values = [day['water'] for day in history]
    elif metric == 'sleep':
        values = [day['sleep'] for day in history]
    elif metric == 'exercise':
        values = [day['exercise'] for day in history]
    elif metric == 'weight':
        values = [day.get('weight_kg') for day in history]  # None for days without log → gap in chart
        
    return jsonify({
        'labels': labels,
        'values': values
    })

@api_bp.route('/api/charts/correlation/<string:corr_type>')
@login_required
def correlation_chart_data(corr_type):
    """
    Provides dual-metric datasets for frontend multi-axis correlation charts.

    Supported correlation types:
    - 'sleep_mood': Compares sleep duration against user-reported mood scores.
    - 'exercise_sleep': Compares exercise duration against sleep duration.

    Args:
        corr_type (str): The identifier for the metric pair comparison.

    Returns:
        JSON response containing date labels and dual data series.
    """
    # Validate requested correlation type
    if corr_type not in ['sleep_mood', 'exercise_sleep']:
        return jsonify({'error': 'Invalid correlation type'}), 400

    # Read date range arguments from client query string
    date_range = request.args.get('range', '30days')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Query log history via service abstraction
    data = HistoryService.get_history_data(current_user.id, date_range, start_date, end_date)
    history = data['history']
    
    # Sort chronological
    history.sort(key=lambda x: x['date'])
    
    # Construct X-axis formatted date strings
    labels = [day['date'].strftime('%b %d') for day in history]
    
    # Build paired metric arrays based on correlation requested
    if corr_type == 'sleep_mood':
        sleep_values = [day['sleep'] for day in history]
        # Perform null-checks on mood entries to safely handle unlogged days (default to 0)
        mood_values = [day['log'].mood_score if (day['log'] and day['log'].mood_score is not None) else 0 for day in history]
        return jsonify({
            'labels': labels,
            'sleep': sleep_values,
            'mood': mood_values
        })
    elif corr_type == 'exercise_sleep':
        exercise_values = [day['exercise'] for day in history]
        sleep_values = [day['sleep'] for day in history]
        return jsonify({
            'labels': labels,
            'exercise': exercise_values,
            'sleep': sleep_values
        })

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from app.services.image_analysis_service import ImageAnalysisService
from app.services.meal_service import allowed_file

@api_bp.route('/api/meals/analyze_upload', methods=['POST'])
@login_required
def analyze_uploaded_meal_image():
    """
    Handles user image uploads for automated meal image recognition and analysis.

    Validates file upload integrity and file extensions, temporarily saves the 
    image locally, triggers computer vision analysis via ImageAnalysisService, and 
    ensures the temporary file is safely cleaned up after processing.

    Returns:
        JSON response containing predicted meal items and nutritional information.
    """
    # Confirm image key is included in request multipart form data
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided.'}), 400
        
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file.'}), 400
        
    # Verify file extension against allowed security list
    if not allowed_file(image_file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type.'}), 400
        
    # Sanitize original filename and append UUID to prevent duplicate naming collisions on disk
    filename = secure_filename(image_file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"temp_{uuid.uuid4().hex}.{ext}"
    
    # Ensure static local upload directory exists
    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'meals')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save image temporarily to server disk for model input
    relative_path = f"uploads/meals/{unique_filename}"
    absolute_path = os.path.join(current_app.static_folder, relative_path)
    image_file.save(absolute_path)
    
    # Run analysis
    success, analysis_result = ImageAnalysisService.analyze_meal_image(relative_path)
    
    # Delete temporary file to maintain server storage cleanliness
    try:
        os.remove(absolute_path)
    except Exception as e:
        pass
        
    # Return structured JSON result back to frontend caller
    if success:
        return jsonify({'success': True, 'data': analysis_result})
    else:
        return jsonify({'success': False, 'error': analysis_result}), 500
