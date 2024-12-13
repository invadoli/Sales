from flask import Blueprint, render_template, jsonify
import sqlite3  # Make sure to import sqlite3

car_blueprint = Blueprint('car_blueprint', __name__, template_folder='templates')


def get_db_connection():
    conn = sqlite3.connect('car_sales_data.db')  # Ensure correct path to your DB file
    conn.row_factory = sqlite3.Row
    return conn


@car_blueprint.route('/', methods=['GET'])
def car():
    conn = get_db_connection()
    try:
        cars = conn.execute('SELECT * FROM car_sales').fetchall()
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

    return render_template('Car/cars.html', cars=cars)


# Debugging route to check database tables and schema
@car_blueprint.route('/debug/db', methods=['GET'])
def debug_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Prepare the output
    db_info = {"tables": tables}

    # If 'car_sales' exists, fetch its schema
    if ('car_sales',) in tables:
        cursor.execute("PRAGMA table_info(car_sales);")
        schema = cursor.fetchall()
        db_info["car_sales_schema"] = schema
    else:
        db_info["car_sales_schema"] = "Table 'car_sales' does not exist."

    conn.close()
    return jsonify(db_info)
