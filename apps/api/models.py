from flask import Blueprint, jsonify, request

# Define the blueprint for the API
api_blueprint = Blueprint('api_blueprint', __name__, template_folder='templates')

@api_blueprint.route('/users', methods=['GET'])
def users():
    from apps.authentication.formed import User

    # Retrieve all users
    users = User.query.all()

    # Serialize user data
    users_data = [
        {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "password": user.password
        }
        for user in users
    ]

    return jsonify(users=users_data)

@api_blueprint.route('/users/<int:user_id>', methods=['GET'])
def user_By_Id(user_id):
    from apps import db
    from apps.authentication.formed import User

    # Retrieve a single user by ID
    user = User.query.get_or_404(user_id)

    # Create the response as a dictionary
    user_data = {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "password": user.password
    }

    # No need to commit session for read operations
    # db.session.commit() is not necessary for GET requests

    return jsonify({"message": f"User with ID {user_id}", "user": user_data}), 200

@api_blueprint.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete(user_id):
    from apps import db
    from apps.authentication.formed import User

    # Retrieve user by ID
    user = User.query.get_or_404(user_id)

    # Delete user
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"User with ID {user_id} deleted successfully"}), 200

@api_blueprint.route('/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    from apps import db
    from apps.authentication.formed import User

    # Retrieve the user by ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get JSON data from the request
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input. No data provided."}), 400

    # Update user fields
    user.name = data.get('name', user.name)
    user.surname = data.get('surname', user.surname)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)

    # Commit changes to the database
    db.session.commit()

    return jsonify({"message": "User updated successfully"}), 200
