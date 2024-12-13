from flask import Blueprint

blueprint = Blueprint(
    'car_blueprint',
    __name__,
    url_prefix='/car'
)

def register_routes():
    # Delay the import to avoid circular import
    from . import routes
