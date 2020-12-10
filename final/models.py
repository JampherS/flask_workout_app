from flask_login import LoginManager, current_user, login_user
from .db import mongo
from .log import login_manager

class User:
	def __init__(self, email, name):
		self.email = email
		self.name = name

	@staticmethod
	def is_authenticated():
		return True

	@staticmethod
	def is_active():
		return True

	@staticmethod
	def is_anonymous():
		return False

	def get_id(self):
 		return self.email

	def get_name(self):
		return self.name

	@login_manager.user_loader
	def load_user(email):
		u = mongo.db.users.find_one({"email": email})
		if not u:
			return None
		return User(email=u['email'], name=u['name'])

