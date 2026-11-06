"""
Custom Route Decorators
-----------------------
This module provides reusable view function decorators for the application.
Specifically, it contains authorization helpers such as `admin_required`
to restrict sensitive management routes to users with the 'admin' role.
"""

from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """
    Custom decorator to restrict route access exclusively to administrators.
    
    If the current visiting user is not logged in or does not have the 'admin' role,
    the request is immediately terminated with an HTTP 403 (Forbidden) error.

    Parameters:
        f (function): The original Flask route view function to wrap.

    Returns:
        function: The protected wrapped function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check 1: Ensure user is logged in (authenticated)
        # Check 2: Ensure user role is explicitly set to 'admin'
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)  # HTTP 403 Forbidden: Access denied
        
        # User is an authenticated admin, proceed to the requested view
        return f(*args, **kwargs)
    return decorated_function

