from flask import Blueprint, render_template

# Define the blueprint for the home section
home_blueprint = Blueprint('home_blueprint', __name__, template_folder='templates')

@home_blueprint.route('/', methods=['GET'])
def index():
    return render_template('home/index.html')

@home_blueprint.route('/tables', methods=['GET'])
def tables():
    return render_template('home/tables.html')

@home_blueprint.route('/notifications', methods=['GET'])
def notifications():
    return render_template('home/notifications.html')

