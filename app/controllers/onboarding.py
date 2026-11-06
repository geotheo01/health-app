"""
Onboarding Controller Blueprint

This module serves as the Controller component within the application's Model-View-Controller (MVC) 
architecture. It handles the multi-step user onboarding workflow for the Smart Health Tracker system.
It processes client HTTP requests, enforces access control based on user roles and status, delegates data 
persistence and business logic calculations to the OnboardingService and ProfileService layers, and 
renders the appropriate HTML view templates.

Author: Computer Science Undergraduate Student
Thesis Project: Smart Health Tracker System
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from app.services.onboarding_service import OnboardingService
from app.services.profile_service import ProfileService

# Instantiate the Flask Blueprint for onboarding routes with a unified URL prefix
onboarding_bp = Blueprint('onboarding', __name__, url_prefix='/onboarding')

@onboarding_bp.route('/')
@login_required
def start():
    """
    Entry point for the onboarding flow.
    
    Evaluates the state of the logged-in user to determine if they need to complete
    the onboarding process or if they should be redirected to an appropriate dashboard.
    """
    # Administrators bypass standard user setup and are sent directly to the admin dashboard
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    # Redirect users who have already finished setup directly to their primary dashboard
    if current_user.onboarding_completed:
        return redirect(url_for('main.dashboard'))
    
    # Send new users to the first step of the onboarding wizard
    return redirect(url_for('onboarding.step', step_num=1))

@onboarding_bp.route('/step/<int:step_num>', methods=['GET', 'POST'])
@login_required
def step(step_num):
    """
    Handles request processing for individual steps (1 through 5) of the onboarding sequence.
    
    Processes POST submissions by validating and persisting user choices through the service layer.
    For GET requests on step 5, calculates recommended baseline health targets based on the user's profile.

    Parameters:
        step_num (int): The current step index in the onboarding wizard sequence.

    Returns:
        Response: A rendered HTML template for GET requests, or a redirect response after POST evaluation.
    """
    # Ensure administrator accounts do not access user setup steps
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    # Prevent previously onboarded users from re-accessing the setup wizard steps
    if current_user.onboarding_completed:
        return redirect(url_for('main.dashboard'))
    
    # Bounds check: Validate that the step number parameter falls within our allowed wizard range [1, 5]
    if step_num < 1 or step_num > 5:
        return redirect(url_for('onboarding.start'))

    # Process user input upon form submission (POST request)
    if request.method == 'POST':
        # Extract form inputs into a flat dictionary structure
        data = request.form.to_dict(flat=True)
        
        # Step 4 contains multi-select checkbox inputs for daily habits; parse list items explicitly
        if step_num == 4:
            habits = request.form.getlist('habits')
            for h in habits:
                data[h] = True
        
        # Delegate data persistence and validation to the service layer
        try:
            success = OnboardingService.save_step_data(current_user.id, step_num, data)
            
            if success:
                # Handle final step completion: update user completion status in DB and grant access to main system
                if step_num == 5:
                    OnboardingService.complete_onboarding(current_user.id)
                    flash("Onboarding complete! Welcome to Smart Health Tracker.", "success")
                    return redirect(url_for('main.dashboard'))
                
                # Step succeeded; proceed sequentially to the next step
                return redirect(url_for('onboarding.step', step_num=step_num + 1))
            else:
                # Feedback to user if server-side validation or persistence failed
                flash("Please correct the errors and try again.", "danger")
        except ValueError as e:
            flash(str(e), "danger")

    # Dynamic target generation for Step 5: Compute tailored baseline goals based on user profile measurements
    suggested_goals = {}
    if step_num == 5:
        profile = ProfileService.get_user_profile(current_user.id)
        if profile:
            # Utilize the service layer algorithm to compute BMR/TDEE suggested caloric intake
            suggested_calories = OnboardingService.calculate_suggested_calories(profile.__dict__)
            suggested_goals = {
                'daily_calorie_goal': suggested_calories,
                'daily_water_goal': 2.0,
                'daily_sleep_goal': 7.0,
                'weekly_exercise_goal': 150
            }

    # Render the template corresponding to the requested step index with calculated context
    return render_template(f'onboarding/step{step_num}.html', step=step_num, suggested_goals=suggested_goals)

@onboarding_bp.route('/finish')
@login_required
def finish():
    """
    Direct route to finalize the onboarding process explicitly.
    
    Updates the user's profile state to mark onboarding as completed and redirects
    to the main application dashboard.
    """
    # Persist the completion state in the database layer via service call
    OnboardingService.complete_onboarding(current_user.id)
    return redirect(url_for('main.dashboard'))
