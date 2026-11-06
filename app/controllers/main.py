"""
Main Blueprint Controller (MVC Architecture)

This module defines the primary routes and controller logic for the application, 
serving as part of the Controller layer in our Flask-based Model-View-Controller (MVC) 
architecture. It manages incoming HTTP requests for public landing pages, user-specific 
dashboards, language switching (i18n), and achievement tracking.

To adhere to the principle of separation of concerns, complex business logic is delegated 
to backend services (such as DashboardService) and helper utilities, keeping the controller 
action handlers lightweight and focused on request orchestration and view rendering.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.services.dashboard_service import DashboardService

# Define the main blueprint instance for primary web routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Render the public landing/index page.

    Serves as the initial entry point for unauthenticated visitors.

    Returns:
        str: Rendered HTML template for the landing page.
    """
    # If the user is already logged in, redirect them directly to their dashboard
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))
        
    # Render the public home page template
    return render_template('index.html')

@main_bp.route('/change_language/<lang>')
def change_language(lang):
    """
    Change the active session language for internationalization (i18n).

    Validates the requested language code against supported options ('el' or 'en') 
    and stores it in the user's session context.

    Args:
        lang (str): The target language code passed via URL parameter.

    Returns:
        werkzeug.wrappers.Response: HTTP redirect to the previous page (HTTP Referrer) 
                                    or fallback to index.
    """
    # Dynamic imports to keep route dependencies scoped locally and prevent potential circular imports
    from flask import session, request
    
    # Input validation: restrict allowed languages to Greek ('el') and English ('en')
    if lang in ['el', 'en']:
        session['lang'] = lang  # Store chosen locale in the current session dictionary
        
    # Redirect back to the referring URL so the user stays on their current page, or fallback to index
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Display the user dashboard page populated with dynamic metrics.

    Requires user authentication via Flask-Login. Delegates data extraction and aggregation 
    logic to the DashboardService layer.

    Returns:
        str: Rendered HTML template for the user dashboard populated with user and service data.
    """
    # Delegate business logic to service layer to retrieve calculated metrics for the current user
    data = DashboardService.get_dashboard_data(current_user.id)
    
    # Render view and inject authenticated user object along with the retrieved dashboard statistics
    return render_template('dashboard/user_dashboard.html', user=current_user, data=data)

@main_bp.route('/achievements')
@login_required
def achievements():
    """
    Display the user's unlocked achievements and progress.

    Requires authentication. Dynamically calculates progress using the achievement utility helper.

    Returns:
        str: Rendered HTML template displaying achievements and gamification data.
    """
    # Lazy import of calculation utility to avoid unnecessary startup overhead
    from app.utils.achievements_util import calculate_achievements
    
    # Compute achievement progress for the currently authenticated user
    data = calculate_achievements(current_user)
    
    # Render achievements page, unpacking the calculated dictionary data into template arguments
    return render_template('main/achievements.html', user=current_user, **data)
