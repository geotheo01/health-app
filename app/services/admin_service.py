"""
admin_service.py
Service layer for handling administrator-related operations on user accounts.
This includes listing all users, toggling active status, changing roles,
updating user credentials/profiles, and safely deleting user accounts.
"""

from app.dao.user_dao import UserDAO


class AdminService:
    """
    Service class providing business logic for administrator user management.
    All methods are static methods since they don't maintain instance state.
    """

    @staticmethod
    def get_all_users():
        """
        Retrieve all registered users from the database.
        Returns a list of User model instances.
        """
        # Fetch all user records via the Data Access Object (DAO)
        return UserDAO.get_all()

    @staticmethod
    def toggle_user_active(user_id):
        """
        Toggle the active/inactive status (ban or unban) of a user account.
        
        Parameters:
            user_id (int): The ID of the user whose status should be flipped.
            
        Returns:
            bool: True if user was found and updated, False otherwise.
        """
        # Look up the user by their ID
        user = UserDAO.get_by_id(user_id)
        if user:
            # Flip the boolean flag for active status
            user.is_active = not user.is_active
            # Save the updated user object back to the database
            UserDAO.save(user)
            return True
        # Return False if the user does not exist
        return False

    @staticmethod
    def change_user_role(user_id, new_role):
        """
        Update the role of a user (for example between 'user' and 'admin').
        
        Parameters:
            user_id (int): The ID of the target user.
            new_role (str): The desired role string ('user' or 'admin').
            
        Returns:
            bool: True if role changed successfully, False if user not found or invalid role.
        """
        # Find the target user
        user = UserDAO.get_by_id(user_id)
        # Validate that user exists and the role is one of the allowed options
        if user and new_role in ['user', 'admin']:
            user.role = new_role
            UserDAO.save(user)
            return True
        return False

    @staticmethod
    def delete_user(user_id, current_admin_id):
        """
        Delete a user account, preventing an admin from deleting themselves.
        
        Parameters:
            user_id (int): The ID of the user to be deleted.
            current_admin_id (int): The ID of the currently logged-in admin.
            
        Returns:
            tuple: (bool success, str message)
        """
        # Prevent self-deletion so an admin doesn't lock themselves out
        if int(user_id) == int(current_admin_id):
            return False, "You cannot delete your own account."
        # Search for the user record to delete
        user = UserDAO.get_by_id(user_id)
        if user:
            # Remove the user record using DAO
            UserDAO.delete(user)
            return True, "User deleted successfully."
        return False, "User not found."

    @staticmethod
    def update_user(user_id, email, username, full_name, password=None):
        """
        Update user profile information from the admin panel, checking for duplicate
        email and username among other users, and optionally setting a new password.
        
        Parameters:
            user_id (int): The ID of the user being edited.
            email (str): New email address.
            username (str): New username.
            full_name (str): New full name.
            password (str, optional): Plaintext password to hash and set, if provided.
            
        Returns:
            tuple: (bool success, str message)
        """
        # Import password hashing utility locally to avoid circular dependencies
        from werkzeug.security import generate_password_hash
        user = UserDAO.get_by_id(user_id)
        if not user:
            return False, "User not found."
            
        # Check if email/username are taken by another user
        existing_email = UserDAO.get_by_email(email)
        if existing_email and existing_email.id != int(user_id):
            return False, "Email already in use by another account."
            
        existing_username = UserDAO.get_by_username(username)
        if existing_username and existing_username.id != int(user_id):
            return False, "Username already in use by another account."

        # Update basic user profile fields
        user.email = email
        user.username = username
        user.full_name = full_name
        
        # If a new password is provided, generate a hash and save it
        if password:
            user.password_hash = generate_password_hash(password)
            
        # Commit changes to the database
        UserDAO.save(user)
        return True, "User updated successfully."
