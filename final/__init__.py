from flask import Flask
from .db_config import workoutsDB, usersDB
from .log import login_manager
from .models import User, Role
from werkzeug.security import generate_password_hash

def create_app():
	app = Flask(__name__)

	app.config['SECRET_KEY'] = 'supersecretkey'
	app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

	workoutsDB.init_app(app)
	usersDB.init_app(app)
	login_manager.init_app(app)

	with app.app_context():
		usersDB.create_all()

		usersDB.session.add(Role(id=0, name='admin'))
		usersDB.session.add(Role(id=1, name='user'))

		admin = User(email='mkoszy@cooper.edu', name='Mark',
				 password=generate_password_hash("password", method='sha256'))
		admin.roles.append(Role.query.filter_by(name='admin').first())

		usersDB.session.add(admin)
		usersDB.session.commit()


	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	return app