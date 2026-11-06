from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from app.dao.user_dao import UserDAO
        return UserDAO.get_by_id(user_id)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @app.context_processor
    def inject_translations():
        from app.utils.translations import translate, get_locale
        lang = get_locale()
        return dict(_=translate, current_lang=lang)

    @app.before_request
    def check_onboarding():
        from flask import request, redirect, url_for
        from flask_login import current_user
        
        # Exclude static files, auth, and onboarding from redirection
        if request.path.startswith('/static/'):
            return
            
        if current_user.is_authenticated and current_user.role != 'admin':
            # Bypass onboarding check during general testing, but allow specific onboarding tests
            from flask import current_app
            if current_app.config.get('BYPASS_ONBOARDING_TEST'):
                return
                
            if not current_user.onboarding_completed:
                # Allowed blueprints
                allowed_blueprints = ['onboarding', 'auth']
                if request.blueprint not in allowed_blueprints:
                    return redirect(url_for('onboarding.start'))

    # Register Blueprints
    from app.controllers.main import main_bp
    app.register_blueprint(main_bp)

    from app.controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.controllers.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.controllers.profile import profile_bp
    app.register_blueprint(profile_bp)

    from app.controllers.onboarding import onboarding_bp
    app.register_blueprint(onboarding_bp)

    from app.controllers.daily_log import logs_bp
    app.register_blueprint(logs_bp)

    from app.controllers.goal import goals_bp
    app.register_blueprint(goals_bp)

    from app.controllers.meal import meals_bp
    app.register_blueprint(meals_bp)

    from app.controllers.history import history_bp
    app.register_blueprint(history_bp)

    from app.controllers.api import api_bp
    app.register_blueprint(api_bp)

    from app.controllers.advisor import advisor_bp
    app.register_blueprint(advisor_bp)

    from app.controllers.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp)

    from app.controllers.errors import errors_bp
    app.register_blueprint(errors_bp)

    from app.cli import seed_admin_command
    app.cli.add_command(seed_admin_command)

    return app
