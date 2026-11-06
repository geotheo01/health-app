"""
Chat Data Access Object (DAO) Module

This module implements the Data Access Object (DAO) pattern for managing chat messages.
In the context of our Flask-based MVC architecture, this class acts as an abstraction 
layer between the business logic (controllers/services) and the database storage layer (SQLAlchemy).
Decoupling database queries into this DAO ensures cleaner, more maintainable code and adheres 
to the Single Responsibility Principle.

Author: CS Senior Thesis Project
"""

from app.models.chat_message import ChatMessage
from app import db


class ChatDAO:
    """
    Data Access Object responsible for all database persistence operations 
    concerning the ChatMessage model.
    """

    @staticmethod
    def get_user_chat_history(user_id):
        """
        Fetches the complete conversation history for a given user.

        The retrieved messages are sorted in ascending order by their creation timestamp 
        to ensure the frontend renders the conversation in correct chronological order.

        Parameters:
            user_id (int/str): The unique identifier of the target user.

        Returns:
            list[ChatMessage]: A list of ChatMessage model instances associated with the user.
        """
        # Query the database for messages matching user_id and sort from oldest to newest
        return ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at.asc()).all()

    @staticmethod
    def save(chat_message):
        """
        Persists a new or updated ChatMessage record into the database.

        Parameters:
            chat_message (ChatMessage): An instance of the ChatMessage model to be persisted.

        Returns:
            ChatMessage: The saved ChatMessage instance (now populated with database-generated 
                         attributes like auto-increment ID and default timestamps).
        """
        # Add the message object to the current SQLAlchemy database session
        db.session.add(chat_message)
        
        # Commit the transaction to permanently store the record in the database
        db.session.commit()
        
        return chat_message
