from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

class CarSales(db.Model):
    __bind_key__ = 'car_sales_db'  # Bind this model to the car_sales_db database
    __tablename__ = 'car_sales'  # Table name should be 'car_sales', not the db name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime(timezone=True), default=db.func.now())
    salesperson = db.Column(db.String(150))
    customer_name = db.Column(db.String(150))
    car_make = db.Column(db.String(150))
    car_model = db.Column(db.String(150))
    car_year = db.Column(db.String(150))
    sale_price = db.Column(db.Float)
    commission_rate = db.Column(db.Float)
    commission_earned = db.Column(db.Float)
