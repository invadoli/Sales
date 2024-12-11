from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from apps.config import Config
from os import path


# Initialize SQLAlchemy and Flask-Login
db = SQLAlchemy()
sales_db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from Config class

    # Initialize the database with the app
    db.init_app(app)

    # Initialize LoginManager with the app
    login_manager.init_app(app)
    login_manager.login_view = 'views.login'  # Redirect to login if the user is not logged in

    # Import models and register routes after db initialization to avoid circular import
    with app.app_context():
        from apps.authentication.formed import User, Note  # Import models here
        # from apps.sales.model import CarSale
        create_database(app)

    from apps.authentication.routes import views
    from apps.home.routes import home_blueprint
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(home_blueprint, url_prefix='/home')


    return app

def create_database(app):
    db_path = path.join('apps', 'data.db')
    if not path.exists(db_path):
        with app.app_context():
            print("Creating tables...")
            db.create_all()  # Create tables in the database
        print(f'Database created at: {db_path}')
    else:
        print(f'Database already exists at: {db_path}')

from apps.authentication.formed import User

# Set up the user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Assuming your User model has an `id` field
    return User.query.get(int(user_id))
