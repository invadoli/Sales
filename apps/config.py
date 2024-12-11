import os

class Config:
    SECRET_KEY = 'Miniminterandksi1.'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'data.db')}"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'car_sales_data.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional but recommended