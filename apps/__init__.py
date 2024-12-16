import os
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from apps.config import Config
from sqlalchemy import inspect
from apps.Car.model import CarSales
from datetime import datetime
# Initialize SQLAlchemy and Flask-Login
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from Config class

    # Initialize the database and LoginManager with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'views.login'  # Redirect to login if the user is not logged in

    # Define the path to your CSV file
    csv_file_path = os.path.join(os.path.dirname(__file__), 'car_Sales_data.csv')

    # Import models and register routes after initializing extensions
    with app.app_context():
        from apps.authentication.formed import User, Note
        create_database(app, csv_file_path)

    # Register blueprints
    from apps.authentication.routes import views
    from apps.home.routes import home_blueprint
    from apps.api.models import api_blueprint
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(home_blueprint, url_prefix='/home')
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app


def create_database(app, csv_file_path):
    car_sales_db_path = os.path.join(app.config['BASE_DIR'], 'car_sales_data.db')

    with app.app_context():
        # Ensure the database file exists
        if not os.path.exists(car_sales_db_path):
            print("Creating car_sales_data.db...")
            os.makedirs(os.path.dirname(car_sales_db_path), exist_ok=True)

        try:
            # Get the engine for the 'car_sales_db' bind
            engine = db.get_engine(app, bind='car_sales_db')

            # Use sqlalchemy.inspect to check if the 'car_sales' table exists
            inspector = inspect(engine)
            if not inspector.has_table('car_sales'):
                # Create the CarSales table
                CarSales.__table__.create(engine)
                print("CarSales table created in car_sales_data.db.")
            else:
                print("CarSales table already exists in car_sales_data.db.")

            # Now that the table exists, let's import the CSV data
            import_csv_to_db(app, csv_file_path)

        except Exception as e:
            print(f"Error creating CarSales table in car_sales_data.db: {e}")


def import_csv_to_db(app, csv_file_path):
    # Read the CSV into a pandas DataFrame
    data = pd.read_csv(csv_file_path)

    # Print the columns to verify them
    print("Columns in CSV file:", data.columns)

    # Define the required columns matching the CSV column names
    required_columns = [
        'Date', 'Salesperson', 'Customer Name', 'Car Make', 'Car Model',
        'Car Year', 'Sale Price', 'Commission Rate', 'Commission Earned'
    ]

    # Check if all required columns are present in the CSV
    if not all(col in data.columns for col in required_columns):
        print('Error: Missing column/s in CSV')
        return

    # Start the Flask app context
    with app.app_context():
        try:
            # Add each row from the CSV to the CarSales table
            for _, row in data.iterrows():
                # Convert the 'Date' column to datetime
                date = pd.to_datetime(row['Date'], errors='coerce')  # `errors='coerce'` will turn invalid dates into NaT (Not a Time)

                # Check if the date conversion was successful
                if pd.isna(date):
                    print(f"Skipping row with invalid date: {row['Date']}")
                    continue  # Skip this row if the date is invalid

                car_sale = CarSales(
                    date=date,  # Use the converted datetime
                    salesperson=row['Salesperson'],
                    customer_name=row['Customer Name'],
                    car_make=row['Car Make'],
                    car_model=row['Car Model'],
                    car_year=row['Car Year'],
                    sale_price=row['Sale Price'],
                    commission_rate=row['Commission Rate'],
                    commission_earned=row['Commission Earned']
                )

                # Add the car sale record to the session
                db.session.add(car_sale)

            # Commit the session to save the data to the database
            db.session.commit()
            print("Data successfully imported into the database.")

        except Exception as e:
            db.session.rollback()  # Rollback the transaction in case of error
            print(f"Error importing data: {e}")


# Set up the user loader function for Flask-Login
from apps.authentication.formed import User

@login_manager.user_loader
def load_user(user_id):
    # Assuming your User model has an `id` field
    return User.query.get(int(user_id))
