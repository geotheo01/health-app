"""
User Model
----------
This module defines the primary User model for the application.
It inherits from Flask-Login's UserMixin to handle session authentication,
login state, and access control. It stores basic account credentials,
user roles ('user' or 'admin'), and onboarding progress flags.
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """
    Represents a registered user in our health application.
    Integrates with Flask-Login to manage user sessions and permissions.
    """
    # Name of the database table
    __tablename__ = 'users'

    # Primary key identifier for the user
    id = db.Column(db.Integer, primary_key=True)

    # Unique email and username used for identification and logging in
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)

    # User's display / full name
    full_name = db.Column(db.String(100), nullable=False)

    # Securely hashed password (never stored in plain text!)
    password_hash = db.Column(db.String(256), nullable=False)

    # Role used for authorization (e.g., 'user' or 'admin')
    role = db.Column(db.String(20), nullable=False, default='user')

    # Account status flags
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Can be toggled by admins
    onboarding_completed = db.Column(db.Boolean, default=False, nullable=False)  # Tracks if initial wizard is done

    # Account creation timestamp stored in UTC
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, **kwargs):
        """
        Custom constructor for the User model.
        If a username is not explicitly provided, it defaults to the local part of the email address.
        """
        # Convenient helper: if username is missing, take the part before the '@' symbol
        if 'email' in kwargs and 'username' not in kwargs:
            kwargs['username'] = kwargs['email'].split('@')[0]
        # Call the parent db.Model constructor with the processed keyword arguments
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        """
        Returns a developer-friendly string representation of the User object,
        useful for debugging and logging in the Flask shell.
        """
        return f'<User {self.username}>'

