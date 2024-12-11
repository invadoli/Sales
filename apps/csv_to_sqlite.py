import sqlite3
import csv
import os

def sanitize_header(header):
    return header.strip().replace(" ", "_").replace("-", "_")

def csv_to_sqlite(csv_path, sqlite_path):
    table_name = "car_sales"
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)

        # Sanitize headers
        sanitized_headers = [sanitize_header(h) for h in headers]

        # Create table
        cursor.execute(f"CREATE TABLE {table_name} ({', '.join(f'{h} TEXT' for h in sanitized_headers)});")

        # Insert data
        for row in reader:
            cursor.execute(
                f"INSERT INTO {table_name} VALUES ({', '.join('?' for _ in sanitized_headers)});", row
            )

    conn.commit()
    conn.close()

csv_path = "apps/car_sales_data.csv"
sqlite_path = "apps/car_sales_data.db"

try:
    csv_to_sqlite(csv_path, sqlite_path)
    print("CSV data has been successfully converted to SQLite database.")
except Exception as e:
    print(f"Error: {e}")


if __name__ == "__main__":
    csv_path = "apps/car_sales_data.csv"  # Path to the CSV file
    sqlite_path = "apps/car_sales.db"    # Path to the new SQLite file
    csv_to_sqlite(csv_path, sqlite_path)
