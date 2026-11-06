"""
Profile Service Module.

This service manages reading and updating user profile information, such as:
- Age and gender
- Height and weight
- Activity level (e.g. sedentary, active)
- Primary health goal (e.g. lose weight, gain muscle)

It handles the 'upsert' logic: finding an existing profile record or creating
a new one if it's the user's first time setting up their profile.
"""

from app.dao.profile_dao import ProfileDAO
from app.models.profile import UserProfile

class ProfileService:
    """
    ProfileService provides methods to access and update a user's biometric
    and fitness profile details in the database.
    """

    @staticmethod
    def get_user_profile(user_id):
        """
        Fetches the profile record for a given user ID.

        Parameters:
            user_id (int): The ID of the user.

        Returns:
            UserProfile or None: The user's profile object, or None if not found.
        """
        # Look up profile by user ID via the DAO
        return ProfileDAO.get_by_user_id(user_id)

    @staticmethod
    def update_or_create_profile(user_id, data):
        """
        Updates an existing user profile or creates a new profile row if none exists yet.

        Parameters:
            user_id (int): The ID of the user.
            data (dict): Dictionary with optional keys: 'age', 'gender', 'height_cm',
                         'weight_kg', 'activity_level', 'health_goal'.

        Returns:
            UserProfile: The saved profile object.
        """
        # Check if the user already has an existing profile record
        profile = ProfileDAO.get_by_user_id(user_id)
        if not profile:
            # If no profile exists yet, create a new UserProfile instance for this user
            profile = UserProfile(user_id=user_id)
        
        # Update each field only if it was included in the data dictionary
        if 'age' in data and data['age'] is not None:
            age = int(data['age'])
            if not (10 <= age <= 120):
                raise ValueError("Η ηλικία πρέπει να είναι μεταξύ 10 και 120 ετών.")
            profile.age = age
        if 'gender' in data: profile.gender = data.get('gender')
        if 'height_cm' in data and data['height_cm'] is not None:
            height = float(data['height_cm'])
            if not (120 <= height <= 230):
                raise ValueError("Το ύψος πρέπει να είναι μεταξύ 120 και 230 cm.")
            profile.height_cm = height
        if 'weight_kg' in data and data['weight_kg'] is not None:
            weight = float(data['weight_kg'])
            if not (40 <= weight <= 230):
                raise ValueError("Το βάρος πρέπει να είναι μεταξύ 40 και 230 kg.")
            profile.weight_kg = weight
        if 'activity_level' in data: profile.activity_level = data.get('activity_level')
        if 'health_goal' in data: profile.health_goal = data.get('health_goal')
        
        # Persist changes to the database and return the saved model
        return ProfileDAO.save(profile)
