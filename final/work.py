from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .db_config import workoutsDB
from .models import is_admin

work = Blueprint('work', __name__)

@work.route('/add')
@login_required
def add():
    exercises = workoutsDB.db.exercises.find({}).sort("name")
    return render_template('exercise.html', exercises=exercises, admin=is_admin(current_user.id))

@work.route('/add', methods=['POST'])
@login_required
def add_post():
    exercise_name = request.form.get('exercise').lower()

    if exercise_name == "":
        flash('Please enter exercise name')
        return redirect(url_for('work.add'))

    exercise = workoutsDB.db.exercises.find_one({"name": exercise_name})
    if exercise:
        flash('Exercise already exists')
        return redirect(url_for('work.add'))

    workoutsDB.db.exercises.insert_one({"name": exercise_name})
    return redirect(url_for('work.add'))

@work.route('/delete/<exercise>', methods=['POST'])
@login_required
def delete(exercise):
    workoutsDB.db.exercises.delete_one({"name": exercise})
    return redirect(url_for('work.add'))

@work.route('/create')
@login_required
def create():
    workouts = workoutsDB.db.workouts.find({}).sort("name")
    return render_template('create_workout.html', workouts=workouts, admin=is_admin(current_user.id))

@work.route('/create', methods=['POST'])
@login_required
def create_post():
    workout_name = request.form.get('workout').lower()

    if workout_name == "":
        flash('Please enter workout name')
        return redirect(url_for('work.create'))

    workout = workoutsDB.db.workouts.find_one({"name": workout_name})
    if workout:
        flash('Workout already exists')
        return redirect(url_for('work.create'))

    workoutsDB.db.workouts.insert_one({"name": workout_name})
    return redirect(url_for('work.append', workout_name=workout_name))

@work.route('/append/<workout_name>')
@login_required
def append(workout_name):
    exercises = workoutsDB.db.exercises.find({}).sort("name")
    return render_template("edit_workout.html", workout_name=workout_name, exercises=exercises)

@work.route('/append/<workout_name>/<exercise_name>', methods=['POST'])
@login_required
def append_post(workout_name, exercise_name):
    order = int(request.form.get('order')) - 1 if request.form.get('order') else None
    weight = float(request.form.get('weight')) if request.form.get('weight') else None
    reps = int(request.form.get('reps')) if request.form.get('reps') else None
    sets = int(request.form.get('sets')) if request.form.get('sets') else None
    time = float(request.form.get('time')) if request.form.get('time') else None
    workouts = workoutsDB.db.workouts.aggregate([
        {"$match": {"name": workout_name}},
        {"$project":
             {"length":
                  {"$size":
                       {"$ifNull" : ["$exercises", []]}
                   }
              }
        }
    ])
    length = 0
    for workout in workouts:
        length = workout['length']

    if order is None:
        flash('Please enter an order')
        return redirect(url_for('work.append', workout_name=workout_name))
    if order > length:
        flash(F'Workout only has {length} exercises right now')
        return redirect(url_for('work.append', workout_name=workout_name))

    workoutsDB.db.workouts.update({"name": workout_name},
                                  {"$push":
                                      {"exercises":
                                          {"$each": [{
                                              "name": exercise_name,
                                              "weight": weight,
                                              "reps": reps,
                                              "sets": sets,
                                              "time": time
                                          }],
                                              "$position": order}
                                      }
                                  })
    return redirect(url_for('work.append', workout_name=workout_name))

@work.route('/remove/<workout>', methods=['POST'])
@login_required
def remove(workout):
    workoutsDB.db.workouts.delete_one({"name": workout})
    return redirect(url_for('work.create'))

@work.route('/workouts')
@login_required
def workouts():
    workouts = workoutsDB.db.workouts.find({}).sort("name")
    return render_template('workout.html', workouts=workouts, admin=is_admin(current_user.id))