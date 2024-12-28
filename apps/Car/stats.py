from datetime import datetime, timedelta
import sys
import matplotlib

matplotlib.use('Agg')
from io import BytesIO
import base64
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

from apps.Car.routes import get_db_connection


def get_car_sales_stats():
    conn = get_db_connection()
    stats = {
        'error': False,
        'message': 'Everything is fine',
    }

    try:
        sql_query = 'SELECT * FROM car_sales'
        df = pd.read_sql_query(sql_query, conn)

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['year'] = df['date'].dt.year

        most_common_year = df['year'].mode()
        most_common_year = (
            most_common_year.iloc[0] if not most_common_year.empty else None
        )


        avg_price = df['sale_price'].mean()
        total_sales = df['sale_price'].sum()
        most_sold_model = (
            df['car_model'].mode().iloc[0] if not df['car_model'].mode().empty else None
        )
        most_spender = df.groupby('customer_name')['sale_price'].sum()
        highest_spender = most_spender.idxmax()  # Get the salesperson with the highest total sales
        highest_sales = most_spender.max()  # Get the amount of the highest total sales
        most_sold_cars = df.groupby('salesperson')['sale_price'].count()
        top_salesperson = most_sold_cars.idxmax()
        top_cars_sold = most_sold_cars.max()
        most_sold = df.groupby('date')['sale_price'].count()
        top_sales = most_sold.idxmax()
        top_date = most_sold.max()
        df['YearMonth'] = df['date'].dt.to_period('M')
        monthly_avg = df.groupby('YearMonth')['sale_price'].mean()
        monthly_avg_pct_change = monthly_avg.pct_change() * 100
        monthly_change = {
            month: f"{pct:.2f}%" for month, pct in monthly_avg_pct_change.items() if pd.notnull(pct)
        }
        total_commission_paid = df['commission_earned'].sum()

        stats.update({
            'avg_price': f"${avg_price:.2f}" if not pd.isna(avg_price) else "No data",
            'total_sales': f"${total_sales:.2f}" if not pd.isna(total_sales) else "No data",
            'most_sold_model': most_sold_model,
            'monthly_avg': monthly_avg.to_dict(),
            'monthly_avg_pct_change': monthly_change,
            'total_commission_paid': f"${total_commission_paid:.2f}",
            'most_common_year': most_common_year if most_common_year is not None else "No data",
            'highest_spender': highest_spender,
            'highest_sales': highest_sales,
            'top_salesperson': top_salesperson,
            'top_cars_sold': top_cars_sold,
            'top_sales' : top_sales,
            'most_sold': most_sold
        })

    except sqlite3.OperationalError as e:
        stats = {'error': True, 'message': f"Failed to load data: {e}"}

    finally:
        conn.close()

    return stats

def get_car_sales_chart():
    conn = get_db_connection()

    try:

        query = "SELECT car_make,SUM(sale_price) as total_sales FROM car_sales GROUP BY car_make"
        df = pd.read_sql_query(query, conn)

        conn.close()

        plt.figure(figsize=(10, 6))
        bars = plt.bar(df['car_make'], df['total_sales'], color='skyblue')

        # Add labels to the bars
        for bar, total in zip(bars, df['total_sales']):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${total:,.2f}",
                     ha='center', va='bottom', fontsize=10)
        # plt.title('Total Sales by Car Make', fontsize=16)
        plt.xlabel('Car Make', fontsize=14)
        plt.ylabel('Total Sales', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save the plot to a BytesIO object and encode it as base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        # Clear the figure to avoid overlapping
        plt.close()

        return chart_base64

    except Exception as e:
        print(f"Error generating car sales chart: {e}")
        return None

def get_monthly_sales_chart():
    conn = get_db_connection()

    try:
        # Fetch the latest date in the dataset
        latest_date_query = "SELECT MAX(date) as latest_date FROM car_sales"
        latest_date_result = pd.read_sql_query(latest_date_query, conn)
        latest_date = latest_date_result['latest_date'].iloc[0]

        if pd.isna(latest_date):
            raise ValueError("No data available in the car_sales table.")

        latest_date = pd.to_datetime(latest_date)

        # Generate last 12 months based on the latest date in the dataset
        months = [(latest_date - timedelta(days=30 * i)).strftime('%Y-%m') for i in range(11, -1, -1)]

        # Fetch sales data grouped by month
        query = """
            SELECT
                strftime('%Y-%m', date) as month,
                SUM(sale_price) as total_sales
            FROM
                car_sales
            WHERE
                date >= date(?, '-12 months')
            GROUP BY
                strftime('%Y-%m', date)
            ORDER BY
                month ASC
        """
        df = pd.read_sql_query(query, conn, params=[latest_date.strftime('%Y-%m-%d')])

        conn.close()

        # Fill missing months with 0 sales
        df.set_index('month', inplace=True)
        df = df.reindex(months, fill_value=0).reset_index()

        # Plot the chart
        plt.figure(figsize=(12, 6))
        bars = plt.bar(df['month'], df['total_sales'], color='steelblue')

        # Annotate bars with sales values
        for bar, total in zip(bars, df['total_sales']):
            # Adjust fontsize and position to avoid overlap
            plt.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 500,  # Add a vertical offset to avoid overlap
                     f"${total:,.2f}",
                     ha='center', va='bottom', fontsize=8)  # Smaller font size

        # plt.title('Monthly Sales for the Last 12 Months', fontsize=16)
        plt.xlabel('Month', fontsize=14)
        plt.ylabel('Total Sales ($)', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save the chart as base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        # Clear the figure
        plt.close()

        return chart_base64

    except Exception as e:
        print(f"Error generating monthly sales chart: {e}")
        return None


def get_car_sales_by_model_chart():
    conn = get_db_connection()

    try:
        # Query to get total sales grouped by car model
        query = """
            SELECT
                car_model,
                SUM(sale_price) as total_sales
            FROM
                car_sales
            GROUP BY
                car_model
            ORDER BY
                total_sales DESC
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        # Check if there is any data
        if df.empty:
            raise ValueError("No sales data available for car models.")

        # Plot the chart
        plt.figure(figsize=(12, 6))
        bars = plt.bar(df['car_model'], df['total_sales'], color='forestgreen')

        # Annotate bars with sales values
        for bar, total in zip(bars, df['total_sales']):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${total:,.2f}",
                     ha='center', va='bottom', fontsize=10)

        plt.title('Total Sales by Car Model', fontsize=16)
        plt.xlabel('Car Model', fontsize=14)
        plt.ylabel('Total Sales ($)', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save the chart as base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        # Clear the figure
        plt.close()

        return chart_base64

    except Exception as e:
        print(f"Error generating car sales by model chart: {e}")
        return None


def get_salesperson_sales_chart():
        conn = get_db_connection()

        try:

            query = "SELECT salesperson, COUNT(*) AS cars_sold FROM car_sales GROUP BY salesperson ORDER BY cars_sold DESC LIMIT 10"
            df = pd.read_sql_query(query, conn)

            conn.close()

            plt.figure(figsize=(10, 6))
            bars = plt.bar(df['salesperson'], df['cars_sold'], color='skyblue')

            # Add labels to the bars
            for bar, total in zip(bars, df['cars_sold']):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{total:,.2f}",
                         ha='center', va='bottom', fontsize=10)
            # plt.title('Total Sales by Car Make', fontsize=16)
            plt.xlabel('SalesPerson', fontsize=14)
            plt.ylabel('Total Cars Sold', fontsize=14)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Save the plot to a BytesIO object and encode it as base64
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()

            # Clear the figure to avoid overlapping
            plt.close()

            return chart_base64

        except Exception as e:
            print(f"Error generating car sales chart: {e}")
            return None

def get_date_sales_chart():
    conn = get_db_connection()

    try:

        query = "SELECT date, COUNT(*) as car_sold FROM car_sales GROUP BY date ORDER BY car_sold DESC LIMIT 10"
        df = pd.read_sql_query(query, conn)

        conn.close()

        plt.figure(figsize=(10,6))
        bars = plt.bar(df['date'], df['car_sold'], color='skyblue')

        for bar, total in zip(bars, df['car_sold']):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                     f"{total:,}", ha='center', va='bottom', fontsize=10)

        plt.xlabel('date', fontsize=14)
        plt.ylabel('car_sold', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        plt.close()

        return chart_base64

    except Exception as e:
        print(f"Error generating car sales chart: {e}")
        return None

def get_costumer_sales_chart():
    conn = get_db_connection()

    try:
        # Query to fetch top 10 customers by total sales
        query = "SELECT customer_name, SUM(sale_price) AS most_costumer FROM car_sales GROUP BY customer_name ORDER BY most_costumer DESC LIMIT 10"
        df = pd.read_sql_query(query, conn)

        conn.close()

        # Create the bar chart
        plt.figure(figsize=(10, 6))
        bars = plt.bar(df['customer_name'], df['most_costumer'], color='skyblue')

        # Add labels to each bar
        for bar, total in zip(bars, df['most_costumer']):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                     f"{total:,.2f}", ha='center', va='bottom', fontsize=10)

        # Update axis labels to reflect the data
        plt.xlabel('Customer', fontsize=14)
        plt.ylabel('Total Sales ($)', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save the chart as a PNG image in memory
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        # Close the plot to avoid memory issues
        plt.close()

        return chart_base64

    except Exception as e:
        print(f"Error generating car sales chart: {e}")
        return None

def get_car_sales_chart1():
    conn = get_db_connection()

    try:
        query = "SELECT car_make, SUM(sale_price) AS total_sales FROM car_sales GROUP BY car_make"
        df = pd.read_sql_query(query, conn)

        conn.close()

        if df.empty:
            print("Error: No data available for chart generation.")
            return None

        plt.figure(figsize=(3, 3))

        # Create the pie chart
        wedges, texts, autotexts = plt.pie(
            df['total_sales'],
            labels=df['car_make'],
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.tab20.colors
        )

        # Adjust font sizes for text labels and percentage labels
        for text in texts:
            text.set_fontsize(10)  # Corrected typo here
        for autotext in autotexts:  # Fixed typo here
            autotext.set_fontsize(10)
            autotext.set_color('white')

        # Adjust layout for tight rendering
        plt.tight_layout()

        # Save the plot to a BytesIO object and encode it as base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        # Clear the figure to avoid overlapping
        plt.close()

        if chart_base64:
            print("Chart base64 generated successfully.")
        else:
            print("Error: No chart generated.")

        return chart_base64

    except Exception as e:
        print(f"Error generating car sales chart: {e}")
        return None


def get_monthly_sales_chart1():
    conn = get_db_connection()

    try:
        # Fetch the latest date in the dataset
        latest_date_query = "SELECT MAX(date) as latest_date FROM car_sales"
        latest_date_result = pd.read_sql_query(latest_date_query, conn)
        latest_date = latest_date_result['latest_date'].iloc[0]

        if pd.isna(latest_date):
            raise ValueError("No data available in the car_sales table.")

        latest_date = pd.to_datetime(latest_date)

        # Generate last 12 months based on the latest date in the dataset
        months = [(latest_date - timedelta(days=30 * i)).strftime('%Y-%m') for i in range(11, -1, -1)]

        # Fetch sales data grouped by month
        query = """
                SELECT
                    strftime('%Y-%m', date) as month,
                    SUM(sale_price) as total_sales
                FROM
                    car_sales
                WHERE
                    date >= date(?, '-12 months')
                GROUP BY
                    strftime('%Y-%m', date)
                ORDER BY
                    month ASC
            """
        df = pd.read_sql_query(query, conn, params=[latest_date.strftime('%Y-%m-%d')])

        conn.close()

        # Fill missing months with 0 sales
        df.set_index('month', inplace=True)
        df = df.reindex(months, fill_value=0).reset_index()

        # Plot the chart (Line Chart)
        plt.figure(figsize=(12, 9))
        plt.plot(df['month'], df['total_sales'], marker='o', color='steelblue', linestyle='-', linewidth=2,
                 markersize=6)

        # Annotate each point with sales values
        for i, total in enumerate(df['total_sales']):
            plt.text(df['month'][i], total + 500, f"${total:,.2f}", ha='center', va='bottom', fontsize=8)

        # Set labels and title
        plt.xlabel('Month', fontsize=14)
        plt.ylabel('Total Sales ($)', fontsize=14)
        plt.title('Monthly Sales for the Last 12 Months', fontsize=16)

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')

        # Apply tight layout to avoid clipping
        plt.tight_layout()

        # Save the chart as base64
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        # Clear the figure to release memory
        plt.close()

        return chart_base64

    except Exception as e:
        print(f"Error generating monthly sales chart: {e}")
        return None