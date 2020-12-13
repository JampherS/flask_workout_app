from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .db_config import usersDB, workoutsDB
from .models import User, Role

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
	return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
	email = request.form.get('email')
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False

	user = User.query.filter_by(email=email).first()

	if not user or not check_password_hash(user.password, password):
		flash('Login was not correct')
		return redirect(url_for('auth.login'))

	login_user(user, remember=remember)
	return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
	return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
	email = request.form.get('email')
	name = request.form.get('name')
	password = request.form.get('password')

	user = User.query.filter_by(email=email).first()

	if user:
		flash('Email Address already exists, please login')
		return redirect(url_for('auth.signup'))
	hashed_pass = generate_password_hash(password, method='sha256')

	new_user = User(email=email, name=name, password=hashed_pass)
	assigned_role = Role.query.filter_by(name='user').first()
	new_user.roles.append(assigned_role)
	usersDB.session.add(new_user)
	usersDB.session.commit()

	workoutsDB.db.tracker.insert_one({"_id": new_user.id})
	return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.index'))