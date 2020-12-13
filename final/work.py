import re
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .db_config import workoutsDB
from .models import is_admin

work = Blueprint('work', __name__)

@work.route('/add')
@login_required
def add():
    exercises = workoutsDB.db.exercises.find({}).sort("name")
    return render_template('exercises.html', exercises=exercises, admin=is_admin(current_user.id))

@work.route('/add', methods=['POST'])
@login_required
def add_post():
    exercise_name = request.form.get('exercise').lower()
    exercise_note = request.form.get('notes') if request.form.get('notes') else None

    if exercise_name == "":
        flash('Please enter exercise name')
        return redirect(url_for('work.add'))

    id = re.sub(r'\W+', '', exercise_name)

    exercise = workoutsDB.db.exercises.find_one({"_id": str(id)})
    if exercise:
        flash('Exercise already exists')
        return redirect(url_for('work.add'))

    workoutsDB.db.exercises.insert_one({"_id": str(id), "name": exercise_name, "notes": exercise_note})
    return redirect(url_for('work.add'))

@work.route('/delete/<exercise_name>')
@login_required
def delete(exercise_name):
    id = re.sub(r'\W+', '', exercise_name)
    workoutsDB.db.exercises.delete_one({"_id": str(id)})
    workoutsDB.db.workouts.update({}, {"$pull": {"exercises": {"name": exercise_name}}})
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

    id = re.sub(r'\W+', '', workout_name)

    workout = workoutsDB.db.workouts.find_one({"_id": str(id)})
    if workout:
        flash('Workout already exists')
        return redirect(url_for('work.create'))

    workoutsDB.db.workouts.insert_one({"_id": str(id), "name": workout_name})
    return redirect(url_for('work.append', workout_name=workout_name))

@work.route('/append/<workout_name>')
@login_required
def append(workout_name):
    id = re.sub(r'\W+', '', workout_name)
    workout_exercises = workoutsDB.db.workouts.find_one({"_id": str(id)})
    exercises = workoutsDB.db.exercises.find({}).sort("name")
    return render_template("edit_workout.html", workout_name=workout_name, workout_exercises=workout_exercises, exercises=exercises, admin=is_admin(current_user.id))

@work.route('/append/<workout_name>/<exercise_name>', methods=['POST'])
@login_required
def append_post(workout_name, exercise_name):
    try:
        order = int(request.form.get('order')) - 1 if request.form.get('order') else None
        weight = float(request.form.get('weight')) if request.form.get('weight') else None
        reps = int(request.form.get('reps')) if request.form.get('reps') else None
        sets = int(request.form.get('sets')) if request.form.get('sets') else None
        time = float(request.form.get('time')) if request.form.get('time') else None
    except:
        flash("Please enter (a) valid response(s)")
        return redirect(url_for('work.append', workout_name=workout_name))

    id = re.sub(r'\W+', '', workout_name.lower())

    workouts = workoutsDB.db.workouts.aggregate([
        {"$match": {"_id": str(id)}},
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

    if order is None or order < 0:
        flash('Please enter a valid order')
        return redirect(url_for('work.append', workout_name=workout_name))
    if order > length:
        flash(F'Workout only has {length} exercises right now')
        return redirect(url_for('work.append', workout_name=workout_name))

    workoutsDB.db.workouts.update({"_id": str(id)},
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

@work.route('/remove/<workout_name>')
@login_required
def remove(workout_name):
    id = re.sub(r'\W+', '', workout_name.lower())
    workoutsDB.db.workouts.delete_one({"_id": str(id)})
    return redirect(url_for('work.create'))

@work.route('/pop/<workout_name>/<index>')
@login_required
def pop(workout_name, index):
    index = int(index) - 1
    filt = F"exercises.{index}"

    id = re.sub(r'\W+', '', workout_name.lower())

    workoutsDB.db.workouts.update_one({"_id": str(id)},
                                      {"$unset":
                                           {filt: 1}})
    workoutsDB.db.workouts.update_one({"_id": str(id)},
                                      {"$pull":
                                           {"exercises": None}})
    return redirect(url_for('work.append', workout_name=workout_name))

@work.route('/exe/<exercise_name>')
@login_required
def exercise(exercise_name):
    id = re.sub(r'\W+', '', exercise_name.lower())
    exercise = workoutsDB.db.exercises.find_one({"_id": str(id)})
    return render_template('exercise.html', exercise=exercise)

@work.route('/wor/<workout_name>')
@login_required
def workout(workout_name):
    id = re.sub(r'\W+', '', workout_name.lower())
    workout = workoutsDB.db.workouts.find_one({"_id": str(id)})
    return render_template('workout.html', workout=workout)

@work.route('/workouts')
@login_required
def workouts():
    workouts = workoutsDB.db.workouts.find({}).sort("name")
    return render_template('workouts.html', workouts=workouts, admin=is_admin(current_user.id))

@work.route('/track/<workout_name>', methods=['POST'])
@login_required
def track(workout_name):
    try:
        weight = int(request.form.get('weight')) if request.form.get('weight') else None
    except:
        flash("Please enter a valid response")
        return redirect(url_for('work.workouts'))

    entry = workoutsDB.db.tracker.find_one({"_id": current_user.id,
                                            "history.date": datetime.today().strftime('%Y-%m-%d')})


    if entry:
        flash("Can only log one weigh-in/workout per day")
        return redirect(url_for('work.workouts'))

    if weight is not None and weight > 0:
        workoutsDB.db.tracker.update({"_id": current_user.id},
                                    {"$push":
                                         {"history":
                                             {"$each": [{
                                             "date": datetime.today().strftime('%Y-%m-%d'),
                                             "weight": weight,
                                             "workout": workout_name
                                             }],
                                             "$position": 0}
                                         }
                                    })
    else:
        workoutsDB.db.tracker.update({"_id": current_user.id},
                                     {"$push":
                                         {"history":
                                             {"$each": [{
                                             "date": datetime.today().strftime('%Y-%m-%d'),
                                             "workout": workout_name
                                             }],
                                             "$position": 0}
                                         }
                                     })

    return redirect(url_for('work.workouts'))