from flask import Flask
from .db_config import mongo, db
from .log import login_manager
from .models import User, Role
from werkzeug.security import generate_password_hash

def create_app():
	app = Flask(__name__)

	app.config['SECRET_KEY'] = 'supersecretkey'
	app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

	mongo.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)

	with app.app_context():
		db.create_all()

		db.session.add(Role(id=0, name='admin'))
		db.session.add(Role(id=1, name='user'))

		admin = User(email='mkoszy@cooper.edu', name='Mark Koszykowski',
				 password=generate_password_hash("password", method='sha256'))
		admin.roles.append(Role.query.filter_by(name='admin').first())

		db.session.add(admin)
		db.session.commit()


	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	return app