from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .db import mongo
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
	return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
	email = request.form.get('email')
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False

	login_query = {"email": email}
	user = mongo.db.users.find_one(login_query)

	if not user or not check_password_hash(user['password'], password):
		flash('Login was not correct')
		return redirect(url_for('auth.login'))
	user_obj = User(email=user['email'], name=user['name'])
	login_user(user_obj, remember=remember)
	return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
	return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
	email = request.form.get('email')
	name = request.form.get('name')
	password = request.form.get('password')

	signup_query = {"email": email}
	user = mongo.db.users.find_one(signup_query)

	if user:
		flash('Email Address already exists')
		return redirect(url_for('auth.signup'))
	hashed_pass = generate_password_hash(password, method='sha256')
	new_user = {"email": email, "name": name, "password": hashed_pass}

	mongo.db.users.insert_one(new_user)

	return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.index'))



