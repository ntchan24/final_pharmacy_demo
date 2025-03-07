from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
#way to secure passwords in hash, not plain text
#a hash is a one way function, you can't reverse it
#so you can't get the password from the hash by reversing it
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login',methods = ["GET", "POST"])
def login():
    # data = request.form #when you access in a route, shows info needed to access the route
    # print(data)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #query the database

        user = User.query.filter_by(email=email).first()
        #filter all the users by email, then get the first one
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) #logs in the user, stores in the flask session 
                return redirect(url_for('views.index')) #accesses the views url, redirects user
            else:
                flash('Incorrect password, try again.', category='error')

        else:
            flash('Email does not exist.', category='error')


    return render_template("login.html", user=current_user) #can access the variable text in the html doc

@auth.route('/logout')
@login_required 
#can't access the logout page unless you're logged in
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up',methods = ["GET", "POST"])
def sign_up():

    if request.method == 'POST':
        #get info from the form
        email =request.form.get('email')
        first_name =request.form.get('firstName')
        password1 =request.form.get('password1')
        password2 =request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
            #cant have two users with the same email

        #checks for valid input from user
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash("passwords don't match", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7  characters.', category='error')
        else:
            #add user to database
            new_user = User(email=email, first_name=first_name, password = generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit() #report changes to the session 
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home')) #accesses the views url, redirects user
        

    return render_template("sign_up.html", user = current_user)


