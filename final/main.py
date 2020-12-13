from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import is_admin

main = Blueprint('main', __name__)

@main.route('/')
def index():
	if current_user.is_authenticated:
		admin = is_admin(current_user.id)
	else:
		admin = False
	return render_template('index.html', admin=admin)

@main.route('/profile')
@login_required
def profile():
	return render_template('profile.html', name=current_user.name, admin=is_admin(current_user.id))