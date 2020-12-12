from flask_login import LoginManager, current_user, login_user
from flask_login import UserMixin
from .db_config import mongo, db
from .log import login_manager

# Mongo Implementation

#class User:
#	def __init__(self, email, name):
#		self.email = email
#		self.name = name
#
#	@staticmethod
#	def is_authenticated():
#		return True
#
#	@staticmethod
#	def is_active():
#		return True
#
#	@staticmethod
#	def is_anonymous():
#		return False
#
#	def get_id(self):
#		return self.email
#
#	def get_name(self):
#		return self.name
#
#	@login_manager.user_loader
#	def load_user(email):
#		u = mongo.db.users.find_one({"email": email})
#		if not u:
#			return None
#		return User(email=u['email'], name=u['name'])


# SQL Implementation
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True, nullable=False)
	name = db.Column(db.String(100))
	password = db.Column(db.String(100))

	roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

class Role(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(50))

class UserRoles(db.Model):
	__tablename__ = 'user_roles'
	id = db.Column(db.Integer(), primary_key=True)
	user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
	role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))








