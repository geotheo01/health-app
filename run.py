from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

import os

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Ensure Admin exists
        admin_by_email = User.query.filter_by(email='admin@smarthealth.local').first()
        admin_by_user = User.query.filter_by(username='admin').first()
        if not admin_by_email and not admin_by_user:
            admin = User(
                email='admin@smarthealth.local',
                username='admin',
                full_name='Admin User',
                password_hash=generate_password_hash('123'),
                role='admin',
                onboarding_completed=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin@smarthealth.local / 123")
    
    # Use debug=True only for development
    is_debug = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 3535))
    app.run(host='0.0.0.0', port=port, debug=is_debug)
