"""
Authentication Service Layer
This module acts as the middleman between the Authentication Controller and the UserDAO.
I placed this logic here rather than directly in the controller to keep the codebase clean
and strictly adhere to the MVC architecture. This service is responsible for handling 
secure password hashing and validating user credentials before they interact with the database.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from app.dao.user_dao import UserDAO

class AuthService:
    @staticmethod
    def register_user(username, email, full_name, password):
        """
        Registers a new user in the system.
        Performs validation checks to ensure no duplicate emails or usernames exist.
        
        Args:
            username (str): The desired username
            email (str): The user's email address
            full_name (str): The user's full name
            password (str): The plain-text password from the registration form
            
        Returns:
            tuple: (success_boolean, user_object_or_error_message)
        """
        # Basic validation to ensure all fields are filled
        if not username or not email or not full_name or not password:
            return False, "All fields are required."
        
        # Check if the email already exists in the database
        existing_user_email = UserDAO.get_by_email(email)
        if existing_user_email:
            return False, "Email already registered."
            
        # Check if the username is already taken
        existing_user_username = UserDAO.get_by_username(username)
        if existing_user_username:
            return False, "Username already taken."

        # Securely hash the password using Werkzeug's default PBKDF2 algorithm
        # NEVER store passwords in plain text!
        password_hash = generate_password_hash(password)
        
        # Prepare the dictionary payload for the DAO
        user_data = {
            'username': username,
            'email': email,
            'full_name': full_name,
            'password_hash': password_hash,
            'role': 'user', # Default role for new signups
            'is_active': True # Account is activated by default
        }
        
        # Insert the user into the database
        user = UserDAO.create(user_data)
        return True, user

    @staticmethod
    def authenticate_user(identifier, password):
        """
        Authenticates a user attempting to log in.
        
        Args:
            identifier (str): The username or email entered by the user
            password (str): The plain-text password to verify
            
        Returns:
            tuple: (success_boolean, user_object_or_error_message)
        """
        # Validate that the login form isn't empty
        if not identifier or not password:
            return False, "Username/Email and password are required."
            
        # Retrieve the user object from the database using either their email or username
        user = UserDAO.get_by_email_or_username(identifier)
        
        # Verify if the user exists and if the provided password matches the stored hash
        if not user or not check_password_hash(user.password_hash, password):
            return False, "Invalid credentials."
            
        # Ensure the user hasn't been banned or disabled by an administrator
        if not user.is_active:
            return False, "Account is disabled."
            
        # Authentication successful
        return True, user

