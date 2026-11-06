"""
Chatbot Controller Module

This module defines the Flask Blueprint for the chatbot component within the Model-View-Controller (MVC) 
architecture. It serves as the Controller layer, managing incoming HTTP requests for the AI chatbot page, 
coordinating with underlying services (ChatbotService and DashboardService), and passing the necessary 
data context to the HTML templates for rendering.

Project: AI-Driven Personal Assistant & Dashboard System
Thesis Focus: MVC Web Architecture and LLM Integration
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.services.chatbot_service import ChatbotService

# Registering the chatbot blueprint to encapsulate chatbot-related routing logic
chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot', methods=['GET', 'POST'])
@login_required
def index():
    """
    Main view controller for the chatbot interface.

    Supports dual functionality based on the HTTP request method:
    - POST: Processes new user input, passes non-empty messages to the AI service, 
            and redirects using the Post/Redirect/Get (PRG) pattern to avoid duplicate submissions.
    - GET: Fetches historical conversation records and user dashboard metrics, 
           then renders the main UI template.

    Security:
        Requires active session authentication via the @login_required decorator.
    """
    # Handle user message submission (form POST request)
    if request.method == 'POST':
        user_message = request.form.get('message')
        
        # Sanitize and validate that the submitted string contains non-whitespace content
        if user_message and user_message.strip():
            # Delegate message handling and LLM response generation to the business logic layer
            ChatbotService.process_message(current_user.id, user_message.strip())
            
        # Post/Redirect/Get (PRG) pattern to prevent form re-submission warnings on browser refresh
        return redirect(url_for('chatbot.index'))
        
    # Localized import to prevent potential circular module dependencies during startup
    from app.services.dashboard_service import DashboardService
    
    # Query database records/state via service layer for current user context
    dashboard_data = DashboardService.get_dashboard_data(current_user.id)
    history = ChatbotService.get_chat_history(current_user.id)
    
    # Render view template with context payload
    return render_template('ai/chatbot.html', history=history, data=dashboard_data)


@chatbot_bp.route('/chatbot/send', methods=['POST'])
@login_required
def send():
    """
    AJAX endpoint for sending chatbot messages without full page reload.

    Accepts a JSON POST body with a 'message' field, processes it via the
    ChatbotService, and returns the AI response as JSON for dynamic UI updates.

    Returns:
        JSON: { 'reply': str, 'time': str } on success,
              { 'error': str } on failure.
    """
    from flask import jsonify
    from datetime import datetime

    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    try:
        # Process message through the service layer (stores user msg + AI reply in DB)
        ChatbotService.process_message(current_user.id, user_message)

        # Fetch the latest AI reply from chat history
        history = ChatbotService.get_chat_history(current_user.id)
        # The last non-user message in history is the AI reply
        # sender can be 'bot' or 'assistant' depending on the service
        ai_reply = next(
            (m for m in reversed(history) if m.sender != 'user'),
            None
        )

        reply_text = ai_reply.message if ai_reply else '...'
        reply_time = ai_reply.created_at.strftime('%H:%M') if ai_reply else datetime.now().strftime('%H:%M')

        return jsonify({'reply': reply_text, 'time': reply_time})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
