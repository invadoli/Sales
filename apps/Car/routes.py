from flask import Blueprint, render_template, jsonify
import sqlite3

car_blueprint = Blueprint('car_blueprint', __name__, template_folder='templates')


def get_db_connection():
    conn = sqlite3.connect('apps/car_sales_data.db')  # Ensure correct path to your DB file
    conn.row_factory = sqlite3.Row
    return conn


@car_blueprint.route('/', methods=['GET'])
def car():
    conn = get_db_connection()
    try:
        cars = conn.execute('SELECT * FROM car_sales LIMIT 100').fetchall()
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

    return render_template('home/cars.html', cars=cars)


# Debugging route to check database tables and schema
@car_blueprint.route('/debug/db', methods=['GET'])
def debug_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Prepare the output
    db_info = {"tables": [table[0] for table in tables]}  # Extract table names from tuples

    # Check if 'car_sales' exists and fetch its schema
    if 'car_sales' in db_info['tables']:
        try:
            cursor.execute("SELECT * FROM car_sales LIMIT 1;")  # Simple query to verify table accessibility
            cursor.fetchall()  # Fetch to ensure the query works
            cursor.execute("PRAGMA table_info(car_sales);")  # Fetch schema if table is accessible
            schema = cursor.fetchall()
            db_info["car_sales_schema"] = schema
        except sqlite3.OperationalError as e:
            db_info["car_sales_schema"] = f"Error retrieving schema: {e}"
    else:
        db_info["car_sales_schema"] = "Table 'car_sales' does not exist."

    conn.close()

    # Convert rows to dictionaries for JSON serialization
    # If the schema contains rows, we need to format them as serializable data
    if isinstance(db_info.get("car_sales_schema"), list):
        db_info["car_sales_schema"] = [dict(row) for row in db_info["car_sales_schema"]]

    return jsonify(db_info)
from flask import Blueprint, render_template, jsonify
import sqlite3

car_blueprint = Blueprint('car_blueprint', __name__, template_folder='templates')


def get_db_connection():
    conn = sqlite3.connect('apps/car_sales_data.db')  # Ensure correct path to your DB file
    conn.row_factory = sqlite3.Row
    return conn


@car_blueprint.route('/', methods=['GET'])
def car():
    conn = get_db_connection()
    try:
        cars = conn.execute('SELECT * FROM car_sales LIMIT 100').fetchall()
    except sqlite3.OperationalError as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

    return render_template('home/cars.html', cars=cars)


# Debugging route to check database tables and schema
@car_blueprint.route('/debug/db', methods=['GET'])
def debug_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Prepare the output
    db_info = {"tables": [table[0] for table in tables]}  # Extract table names from tuples

    # Check if 'car_sales' exists and fetch its schema
    if 'car_sales' in db_info['tables']:
        try:
            cursor.execute("SELECT * FROM car_sales LIMIT 1;")  # Simple query to verify table accessibility
            cursor.fetchall()  # Fetch to ensure the query works
            cursor.execute("PRAGMA table_info(car_sales);")  # Fetch schema if table is accessible
            schema = cursor.fetchall()
            db_info["car_sales_schema"] = schema
        except sqlite3.OperationalError as e:
            db_info["car_sales_schema"] = f"Error retrieving schema: {e}"
    else:
        db_info["car_sales_schema"] = "Table 'car_sales' does not exist."

    conn.close()

    # Convert rows to dictionaries for JSON serialization
    # If the schema contains rows, we need to format them as serializable data
    if isinstance(db_info.get("car_sales_schema"), list):
        db_info["car_sales_schema"] = [dict(row) for row in db_info["car_sales_schema"]]

    return jsonify(db_info)
