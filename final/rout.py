from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .main import main
from .db_config import workoutsDB

work = Blueprint('work', __name__)

@work.route('/create')
@login_required
def create():
    #exercises = workoutsDB.db.exercises.find().sort("name")
    exercises = None
    return render_template('create.html', exercises=exercises)

#@rout.route('/create', methods=['POST'])
#def create_post():
#    exercise_name = request.form.get('exercise_name')

#    workout_name = request.form.get('workout_name')


@work.route('/workouts')
@login_required
def workouts():
    return render_template('workout.html')