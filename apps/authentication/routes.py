from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required
from apps.authentication.forms import LoginForm, RegistrationForm
from werkzeug.security import check_password_hash
from apps.authentication.formed import User  # Lazy import of models after app setup

# Define the blueprint
views = Blueprint('views', __name__, template_folder='templates')

@views.route('/', methods=['GET', 'POST'])
def index():
    from apps import db  # Lazy import of db inside the function
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, surname=form.surname.data, email=form.email.data, password=form.password.data)

        db = current_app.extensions['sqlalchemy']
        db.session.add(user)
        db.session.commit()

        print(f"User created: {user.name} {user.surname}, Email: {user.email}")

        flash('Your account has been created!', 'success')

        return redirect(url_for('views.login'))  # Redirect to login page after registration
    return render_template('accounts/register.html', form=form)


@views.route('/login', methods=['GET', 'POST'])
def login():
    from apps import db  # Lazy import of db inside the function
    form = LoginForm()

    if form.validate_on_submit():
        # Query the user by their email
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.password == form.password.data:  # Compare the plain text passwords
            login_user(user)  # Log the user in (requires Flask-Login)
            flash('Login successful', 'success')

            # Print the logged-in user details to the terminal
            print(f"User logged in: {user.name} {user.surname}, Email: {user.email}")

            return redirect(url_for('home_blueprint.index'))  # Redirect to index after successful login
        else:
            flash('Invalid login credentials', 'danger')  # Show an error message if credentials are wrong

    return render_template('accounts/login.html', form=form)


@views.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('views.login'))

