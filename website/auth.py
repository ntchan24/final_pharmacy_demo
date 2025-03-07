from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re

auth = Blueprint('auth', __name__)

# Allowed email domains
ALLOWED_DOMAINS = ['pharmacy.ca', 'gmail.com']

# Email validation function
def is_valid_email(email):
    # Basic email format check
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Domain check
    domain = email.split('@')[1]
    return domain in ALLOWED_DOMAINS

@auth.route('/')
def root():
    if current_user.is_authenticated:
        return redirect(url_for('views.index'))
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database
        user = User.query.filter_by(email=email).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Incorrect password. Please try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        # Get info from the form
        email = request.form.get('email')
        full_name = request.form.get('fullName')
        role = request.form.get('role')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Validate data
        if not is_valid_email(email):
            flash('Invalid email domain. Please use an approved email address.', category='error')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists.', category='error')
        elif len(full_name) < 2:
            flash('Full name must be at least 2 characters.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Add user to database
            new_user = User(
                email=email,
                full_name=full_name,
                role=role,
                password=generate_password_hash(password1, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.index'))

    return render_template("signup.html", user=current_user)