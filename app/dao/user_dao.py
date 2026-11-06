"""
User Data Access Object (DAO).
This file manages all database queries and transactions for the User model.
It provides functions for user registration, authentication lookups, profile management,
and admin metrics such as counting active/inactive users.
"""

from app.models.user import User
from app import db


class UserDAO:
    """
    DAO class handling CRUD operations and queries for user accounts.
    """

    @staticmethod
    def create(user_data):
        """
        Create and persist a new user record from a dictionary of user attributes.
        """
        # Instantiate a new User object unpacking the provided dictionary
        user = User(**user_data)
        # Stage the new user in the database session
        db.session.add(user)
        # Commit the transaction to insert into the database
        db.session.commit()
        # Return the newly created user instance
        return user

    @staticmethod
    def get_by_email(email):
        """
        Look up a user by their email address (used during login and registration checks).
        """
        # Query the users table for the first user matching this email
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username):
        """
        Look up a user by their unique username.
        """
        # Query the users table for the first user matching this username
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email_or_username(identifier):
        """
        Find a user matching either their email address or username (allows flexible login).
        """
        # Check if the identifier matches either the email or the username column
        return User.query.filter((User.email == identifier) | (User.username == identifier)).first()

    @staticmethod
    def get_by_id(user_id):
        """
        Find a user by their primary key ID.
        """
        # Convert user_id to int and look up via session.get
        return db.session.get(User, int(user_id))

    @staticmethod
    def get_all():
        """
        Retrieve all registered users in the system (used in admin dashboards).
        """
        # Fetch all rows from the users table
        return User.query.all()

    @staticmethod
    def count_total():
        """
        Return the total number of registered users.
        """
        # Count all user records in the database
        return User.query.count()

    @staticmethod
    def count_active():
        """
        Return the number of active user accounts.
        """
        # Count users where is_active is set to True
        return User.query.filter_by(is_active=True).count()

    @staticmethod
    def count_inactive():
        """
        Return the number of inactive/disabled user accounts.
        """
        # Count users where is_active is set to False
        return User.query.filter_by(is_active=False).count()

    @staticmethod
    def get_latest(limit=5):
        """
        Retrieve the most recently registered users, up to a specified limit.
        """
        # Order users by registration timestamp descending and take the top results
        return User.query.order_by(User.created_at.desc()).limit(limit).all()

    @staticmethod
    def save(user):
        """
        Add or update an existing user instance and commit the changes.
        """
        # Stage the user model changes in the session
        db.session.add(user)
        # Commit the transaction to persist updates
        db.session.commit()

    @staticmethod
    def delete(user):
        """
        Delete a user account from the database.
        """
        # Mark the user record for deletion
        db.session.delete(user)
        # Commit the transaction to permanently remove the user
        db.session.commit()

