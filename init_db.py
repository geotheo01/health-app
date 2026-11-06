from app import create_app, db
from app.models.user import User
from app.models.daily_log import DailyLog
from app.models.meal import Meal, MealItem
from app.models.goal import Goal
from app.models.favorite_meal import FavoriteMeal

app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
