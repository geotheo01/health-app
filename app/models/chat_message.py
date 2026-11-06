"""
Chat Message Model
This module defines the ChatMessage database model used to store chat
conversations between users and the AI health assistant.
"""

from datetime import datetime
from app import db


class ChatMessage(db.Model):
    """
    Represents an individual message in a chat conversation.
    Stores who sent the message (user or assistant), the message content,
    and references the user who owns this chat history.
    """
    __tablename__ = 'chat_messages'

    # Unique identifier for each chat message
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking the message to the user who owns the conversation
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Indicates who sent the message: either 'user' or 'assistant'
    sender = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'

    # The actual text content of the message
    message = db.Column(db.Text, nullable=False)

    # Timestamp indicating when the message was sent (defaults to current time)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship back to the User model so we can access user.chat_history
    user = db.relationship('User', backref=db.backref('chat_history', lazy=True, cascade='all, delete-orphan'))

