"""
Authentication Controller (Flask Blueprint)

This module manages the HTTP routes associated with user authentication in accordance
with the Model-View-Controller (MVC) architectural pattern. It acts as the Controller layer,
interfacing between the HTTP client views and the backend business logic encapsulated 
within the AuthService class.

Responsibilities:
- Route user registration requests and invoke user creation services.
- Manage authentication sessions (login/logout) using Flask-Login.
- Perform role-based and state-based user redirection post-login.

Author: Computer Science Undergraduate Student
Project: Final Year Thesis Project
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.services.auth_service import AuthService

# Construct the authentication Blueprint for modular routing within the Flask application
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user account registration.

    For GET requests:
        Renders the account registration web form.

    For POST requests:
        Extracts user registration details from form data and passes them to the
        AuthService layer for validation and database persistence. Flashes feedback
        messages based on success or failure of the operation.

    Returns:
        Response: HTML template rendering or HTTP redirection.
    """
    # Check if the incoming request is submitting form data
    if request.method == 'POST':
        # Retrieve submitted payload parameters from request form
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        
        # Delegate account creation logic to the service layer to keep controller light
        success, result = AuthService.register_user(username, email, full_name, password)
        if success:
            # Display success message to user and redirect to login page
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('auth.login'))
        else:
            # Flash error message returned by the service layer (e.g., duplicate email)
            flash(result, "danger")
            
    # Render the registration view template for GET requests or failed POST submissions
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user authentication and session initiation.

    For GET requests:
        Renders the user login interface.

    For POST requests:
        Authenticates user credentials against backend records. Upon successful authentication,
        establishes a session via Flask-Login and dynamically redirects the user based on
        their specific role (e.g., admin vs standard) and onboarding completion state.

    Returns:
        Response: HTML template rendering or HTTP redirection to appropriate dashboard route.
    """
    # Process login attempts on form submit
    if request.method == 'POST':
        # Extract user input (identifier accepts either username or email)
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        
        # Call the authentication service to verify credentials
        success, result = AuthService.authenticate_user(identifier, password)
        if success:
            # Log the user in and set up session cookies via Flask-Login
            login_user(result)
            
            # Route 1: Direct administrator users to the admin control panel
            if result.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            
            # Route 2: Direct new/incomplete users to complete mandatory onboarding
            if not result.onboarding_completed:
                return redirect(url_for('onboarding.start'))
            
            # Route 3: Direct standard authenticated users to their main dashboard
            return redirect(url_for('main.dashboard'))
        else:
            # Flash authentication error (e.g., invalid credentials message)
            flash(result, "danger")
            
    # Render the login view template for GET requests
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Handle user logout and session termination.

    Requires an active authenticated session (@login_required). Destroys current user session
    and redirects user to the login screen.

    Returns:
        Response: Redirect response to the login route.
    """
    # Revoke session cookies and clear Flask-Login user session
    logout_user()
    
    # Redirect user back to authentication entry point
    return redirect(url_for('auth.login'))
