"""
Errors Blueprint Module

This module defines custom error handlers for the Flask web application using a Blueprint.
Within our Model-View-Controller (MVC) architecture, this module operates as a Controller 
component dedicated to handling error states. It intercepts application-wide HTTP status 
codes (403, 404, and 500) and routes them to their corresponding HTML View templates, 
ensuring a graceful degradation of the user interface when errors occur.
"""

from flask import Blueprint, render_template

# Initialize the errors blueprint to register application-wide error handlers
errors_bp = Blueprint('errors', __name__)


@errors_bp.app_errorhandler(403)
def forbidden_error(error):
    """
    Handle HTTP 403 Forbidden errors.

    This handler is invoked when a user attempts to access a protected route or resource
    without the necessary authorization or privileges.

    Args:
        error: The exception object passed automatically by Flask.

    Returns:
        tuple: A tuple containing the rendered 403 HTML template and the 403 HTTP status code.
    """
    # Render the custom 403 template and return the explicit HTTP status code
    return render_template('errors/403.html'), 403


@errors_bp.app_errorhandler(404)
def not_found_error(error):
    """
    Handle HTTP 404 Not Found errors.

    This handler is invoked when a client requests a resource or URL endpoint that does not
    exist on the server.

    Args:
        error: The exception object passed automatically by Flask.

    Returns:
        tuple: A tuple containing the rendered 404 HTML template and the 404 HTTP status code.
    """
    # Render the custom 404 template and return the explicit HTTP status code
    return render_template('errors/404.html'), 404


@errors_bp.app_errorhandler(500)
def internal_error(error):
    """
    Handle HTTP 500 Internal Server errors.

    This handler is triggered when an unhandled server-side exception occurs. It ensures
    database integrity by rolling back any failed or active database transactions before 
    displaying the error page to the user.

    Args:
        error: The exception object passed automatically by Flask.

    Returns:
        tuple: A tuple containing the rendered 500 HTML template and the 500 HTTP status code.
    """
    # Import the database instance locally to prevent circular import issues during initial app setup
    from app import db
    
    # Roll back any pending database operations to reset the session to a clean state
    db.session.rollback()
    
    # Render the custom 500 template and return the explicit HTTP status code
    return render_template('errors/500.html'), 500
