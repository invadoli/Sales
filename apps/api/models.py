from flask import Blueprint, jsonify, request,current_app

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


@api_blueprint.route('/carSales', methods=['GET'])
def get_car_sales():  # Renamed the function to avoid conflict
    from apps.Car.model import CarSales  # Ensure this import is correct and `CarSales` is defined in `apps.Car.model`

    # Retrieve all car sales
    cars = CarSales.query.all()  # No conflict with the function name anymore

    # Serialize car data
    cars_data = [
        {
            "id": car.id,
            "date": car.date,
            "salesperson": car.salesperson,
            "customer_Name": car.customer_Name,
            "car_make": car.car_make,
            "car_model": car.car_model,
            "car_year": car.car_year,
            "sale_price": car.sale_price,
            "commission_rate": car.commission_rate,
            "commission_earned": car.commission_earned,
        }
        for car in cars
    ]

    return jsonify(cars=cars_data)


@api_blueprint.route('/cars/<int:carSales_id>', methods=['GET'])
def carSales_By_ID(carSales_id):
    from apps import db
    from apps.Car.model import CarSales

    # Retrieve a single user by ID
    car = CarSales.query.get_or_404(carSales_id)

    # Create the response as a dictionary
    car_data = {
        "id": car.id,
        "date": car.date,
        "salesperson": car.salesperson,
        "customer_Name": car.customer_Name,
        "car_make":  car.car_make,
        "car_model": car.car_model,
        "car_year": car.car_year,
        "sale_price": car.sale_price,
        "commission_rate" : car.commission_rate,
        "commission_earned": car.commission_earned,
    }

    # No need to commit session for read operations
    # db.session.commit() is not necessary for GET requests

    return jsonify({"message": f"Car Sale  with ID {carSales_id}", "car": car_data}), 200



@api_blueprint.route('/carSales/add', methods=['POST'])
def add_CarSale():
    from apps import db
    from apps.Car.model import CarSales

    # Get JSON data from the request
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input. No data provided."}), 400

    # Validate required fields
    required_fields = [
        "salesperson", "customer_Name", "car_make", "car_model",
        "car_year", "sale_price", "commission_rate", "commission_earned"
    ]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        # Create a new CarSales record
        new_car_sale = CarSales(
            salesperson=data["salesperson"],
            customer_name=data["customer_Name"],
            car_make=data["car_make"],
            car_model=data["car_model"],
            car_year=data["car_year"],
            sale_price=float(data["sale_price"]),
            commission_rate=float(data["commission_rate"]),
            commission_earned=float(data["commission_earned"])
        )

        # Add to the database session and commit
        db.session.add(new_car_sale)
        db.session.commit()

        # Response payload
        car_data = {
            "id": new_car_sale.id,
            "date": new_car_sale.date,
            "salesperson": new_car_sale.salesperson,
            "customer_Name": new_car_sale.customer_name,
            "car_make": new_car_sale.car_make,
            "car_model": new_car_sale.car_model,
            "car_year": new_car_sale.car_year,
            "sale_price": new_car_sale.sale_price,
            "commission_rate": new_car_sale.commission_rate,
            "commission_earned": new_car_sale.commission_earned
        }

        return jsonify({"message": "Car Sale added successfully", "car": car_data}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@api_blueprint.route('/carSales/delete/<int:carSales_id>', methods=['DELETE'])
def delete_CarSale(carSales_id):
    from apps import db
    from apps.authentication.formed import User

    # Retrieve user by ID
    cars = User.query.get_or_404(carSales_id)

    # Delete user
    db.session.delete(cars)
    db.session.commit()

    return jsonify({"message": f"Car Sale with ID {cars} deleted successfully"}), 200

@api_blueprint.route('/carSales/Edit/<int:carSales_id>', methods=['PUT'])
def edit_CarSale(carSales_id):
    from apps import db
    from apps.Car.model import CarSales

    # Retrieve the user by ID
    cars = CarSales.query.get(carSales_id)
    if not cars:
        return jsonify({"error": "User not found"}), 404

    # Get JSON data from the request
    data = request.json
    if not data:
        return jsonify({"error": "Invalid input. No data provided."}), 400

    # Update user fields
    cars.date = data.get('date', cars.date)
    cars.salesperson = data.get('salesperson', cars.salesperson)
    cars.customer_name = data.get('customer_Name', cars.customer_Name)
    cars.car_make = data.get('car_make', cars.car_make)
    cars.car_model = data.get('car_model', cars.car_model)
    cars.car_year = data.get('car_year', cars.car_year)
    cars.sale_price = data.get('sale_price', cars.sale_price)
    cars.commission_rate = data.get('commission_rate', cars.commission_rate)
    cars.commission_earned = data.get('commission_earned', cars.commission_earned)

    # Commit changes to the database
    db.session.commit()

    return jsonify({"message": "User updated successfully"}), 200