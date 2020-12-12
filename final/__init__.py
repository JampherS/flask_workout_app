from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from .db_config import mongo, db
from .log import login_manager

def create_app():
	app = Flask(__name__)

	app.config['SECRET_KEY'] = 'supersecretkey'
	app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

	mongo.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)


	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	return app
