
import re
import pandas as pd
from flask import Blueprint, render_template
import sqlite3

from apps import CarSales
from apps.Car.stats import get_car_sales_stats, get_car_sales_chart1, get_monthly_sales_chart1, \
    get_car_sales_by_model_chart, get_salesperson_sales_chart, get_date_sales_chart

# Define the blueprint for the home section
home_blueprint = Blueprint('home_blueprint', __name__, template_folder='templates')

def get_db_connection():
    conn = sqlite3.connect('apps/car_sales_data.db')
    conn.row_factory =sqlite3.Row
    return conn


@home_blueprint.route('/', methods=['GET'])
def index():
    stats = get_car_sales_stats()
    chart = get_car_sales_chart1()
    total = get_monthly_sales_chart1()
    model_sales_chart = get_car_sales_by_model_chart()
    salesperson = get_salesperson_sales_chart()
    date = get_date_sales_chart()
    if chart:
        print("Chart generated successfully.")
    else:
        print("Chart generation failed.")

    if total:
        print("Monthly Sales Chart base64:", total[:50])  # Print the first 50 chars
    else:
        print("Monthly Sales Chart could not be generated.")
    return render_template('home/index.html', stats=stats, chart=chart, total = total,model_sales_chart = model_sales_chart, salesperson = salesperson, date = date)

@home_blueprint.route('/tables', methods=['GET'])
def tables():
    return render_template('home/tables.html')

@home_blueprint.route('/notifications', methods=['GET'])
def notifications():
    return render_template('home/notifications.html')

@home_blueprint.route('/users', methods=['GET','POST'])
def users():
    from apps import db
    from apps.authentication.formed import User

    users = User.query.all()

    for user in users:
        print(f"User: {user.name} {user.surname}, Email: {user.email}")


    return render_template('home/user.html', users = users)


@home_blueprint.route('/cars', methods=['GET', 'POST'])
def cars():
    try:
        # Fetch all car sales
        cars = CarSales.query.all()

        # Log debug information
        print(f"Number of cars fetched: {len(cars)}")
        for car in cars:
            print(f"Car fetched: {car.salesperson}, {car.car_make}, {car.car_model}")

        return render_template('home/cars.html', cars=cars)

    except Exception as e:
        # Log the exact error to the console
        print(f"Error while fetching car sales data: {e}")
        return "An error occurred while fetching car sales data.", 500


