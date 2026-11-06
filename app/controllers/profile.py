"""
Profile Blueprint Module.

This file acts as the Controller component within our Model-View-Controller (MVC) 
architecture. It handles routing and HTTP requests related to user profile management,
such as viewing and updating profile information. Business logic operations are 
delegated to the ProfileService layer to maintain a clean separation of concerns.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.profile_service import ProfileService

# Initialize the Flask Blueprint for user profile endpoints
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def view():
    """
    Display the currently logged-in user's profile.

    Queries the business service layer for profile data associated with the 
    authenticated user's ID and renders the profile view template.

    Returns:
        str: Rendered HTML page for the user profile view.
    """
    # Fetch user profile data via the service layer using the authenticated user's ID
    profile = ProfileService.get_user_profile(current_user.id)
    
    # Render and return the presentation view with profile context
    return render_template('profile/view.html', profile=profile)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """
    Handle viewing and submitting the profile edit form.

    Supports HTTP GET (to load the current data into the form) and HTTP POST 
    (to validate, parse, and save updated profile attributes).

    Returns:
        Response or str: Redirect response to the profile view on successful POST, 
                         or the rendered profile edit template on GET/failure.
    """
    # Fetch existing profile data to populate form fields if editing
    profile = ProfileService.get_user_profile(current_user.id)
    
    # Check if the request is a form submission
    if request.method == 'POST':
        # Extract form parameters with appropriate data type casting
        data = {
            'age': request.form.get('age', type=int),
            'gender': request.form.get('gender'),
            'height_cm': request.form.get('height_cm', type=float),
            'weight_kg': request.form.get('weight_kg', type=float),
            'activity_level': request.form.get('activity_level'),
            'health_goal': request.form.get('health_goal')
        }
        
        # Persist changes or create a new profile record through the service layer
        try:
            ProfileService.update_or_create_profile(current_user.id, data)
            # Flash a user feedback message and redirect to the read-only profile view page
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.view'))
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('profile.edit'))
    
    # If request method is GET, display the profile editing form
    return render_template('profile/edit.html', profile=profile)
