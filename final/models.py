from flask_login import LoginManager, current_user, login_user
from flask_login import UserMixin
from .db_config import workoutsDB, usersDB
from .log import login_manager

class Exercise:
	def __init__(self, name):
		self.name = name

class Routine:
	def __init__(self, name):
		self.name = name

class User(UserMixin, usersDB.Model):
	id = usersDB.Column(usersDB.Integer, primary_key=True)
	email = usersDB.Column(usersDB.String(100), unique=True, nullable=False)
	name = usersDB.Column(usersDB.String(100))
	password = usersDB.Column(usersDB.String(100))

	roles = usersDB.relationship('Role', secondary='user_roles', backref=usersDB.backref('users', lazy='dynamic'))

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

class Role(usersDB.Model):
	id = usersDB.Column(usersDB.Integer(), primary_key=True)
	name = usersDB.Column(usersDB.String(50))

class UserRoles(usersDB.Model):
	__tablename__ = 'user_roles'
	user_id = usersDB.Column(usersDB.Integer(), usersDB.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
	role_id = usersDB.Column(usersDB.Integer(), usersDB.ForeignKey('role.id', ondelete='CASCADE'))