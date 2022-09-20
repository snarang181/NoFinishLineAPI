from email import message
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
import os, requests, json
from dotenv import load_dotenv
from  api.user_db_management import user_register,check_user_exists, user_login
from api.workout_data_log import past_workouts, get_single_workout_data, workout_log, remove_workout, update_workout
from api.workout_stats import get_workout_stats
from api.individual_workout_data import send_data



load_dotenv()

app = Flask(__name__)
api_key = os.environ.get('API_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')



@app.route('/', methods=['GET'])
def landing():
    data = request.get_json()
    return {'message': 'Hello, World! This is a private API.'}, 200

@app.route('/user/signup', methods=['POST'])
def signup():
    data = request.get_json()
    try:
        if(data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    
    id  = data['id']
    password = data['password']
    age = data['age']
    weight = data['weight']
    first_name = data['first_name']
    last_name = data['last_name']
    status_code, message, auth_token, userid  = user_register(id, password, first_name, last_name, age, weight)
    return {"message": message, "auth_token": auth_token, "userID":str(userid)}, status_code

@app.route('/user/exists', methods=['POST'])
def exists() :
    data = request.get_json()
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    code, message = check_user_exists(request.get_json()['email'])
    return  {"message": message}, code  

@app.route('/user/login', methods=['POST'])
def user_login_app() :
    data = request.get_json()
    user_id = ''
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    try:
        user_id = data['user_id']
        password = data['password']
    except:
        return {"message": "Invalid input"}, 401
    code, data, auth_token, id = user_login(data['user_id'].lower(), data['password'])
    return {"message": data, "auth_token": auth_token, "userID":str(id)}, code
        

@app.route('/user/past_workouts', methods=['POST'])
def past_workouts_route():
    data = request.get_json()
    user_id = ''
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    try:
        user_id = data['user_id']
    except:
        return {"message": "User ID required"}, 401
    code, message = past_workouts(user_id)
    return  {"message": message}, code

@app.route('/user/single_workout', methods=['POST'])
def single_workout_data():
    data = request.get_json()
    user_id = ''
    workout_id = ''
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    try:
        user_id = data['user_id']
        workout_id = data['workout_id']
    except:
        return {"message": "user_id and workout_id required"}, 400
    
    code, message = get_single_workout_data(user_id, workout_id)
    return {"message": message}, code

@app.route('/user/delete_workout', methods=['POST'])
def delete_workout():
    data = request.get_json()
    user_id = ''
    workout_id = ''
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    try:
        user_id = data['user_id']
        workout_id = data['workout_id']
    except:
        return {"message": "user_id and workout_id required"}, 400
    code, message = remove_workout(user_id, workout_id)
    return {"message": message}, code

@app.route('/user/update_workout', methods=['POST'])
def user_update_workout():
    data = request.get_json()
    user_id = ''
    workout_id = ''
    workout_name = ''
    workout_calories_burnt = ''
    workout_duration = ''
    workout_notes = ''
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    try:
        user_id = data['user_id']
        workout_id = data['workout_id']
        workout_name = data['workout_name']
        workout_duration = data['workout_duration']
        workout_calories_burnt = data['workout_calories_burnt']
        workout_notes = data['workout_notes']
        workout_date = data['workout_date']
        code, message = update_workout(user_id, workout_id, workout_name, workout_duration, workout_calories_burnt, workout_notes, workout_date)
        return {"message": message}, code
    except Exception as e:
        return {"message": str(e)}, 400

@app.route('/user/workout_log', methods=['POST'])
def log_workout():
    data = request.get_json()
    user_id = ''
    workout_name = ''
    workout_calories_burnt = ''
    workout_duration = ''
    workout_notes = ''
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    try:
        user_id = data['user_id']
        workout_name = data['workout_name']
        workout_duration = data['workout_duration']
        workout_calories_burnt = data['workout_calories_burnt']
        workout_notes = data['workout_notes']
    except:
        return {"message": "All fields reqd"}, 400
    code, message = workout_log(user_id, workout_name, workout_duration, workout_calories_burnt, workout_notes)
    return {"message": message}, code

@app.route('/user/workout_stats', methods=['POST'])
def workout_stats():
    data = request.get_json()
    user_id = ''
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    try:
        user_id = data['user_id']
    except: 
        return {"message": "user_id required"}, 400
    code, message = get_workout_stats(user_id)
    return {"message": message}, code

@app.route('user/workout_details', methods=['POST'])
def workout_details():
    data = request.get_json()
    workout_name = ''
    try:
        if (data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    try:
        workout_name = data['workout_name']
    except: 
        return {"message": "Workout nmae required"}, 400
    code, message = send_data(workout_name)
    return {"message": message}, code






    





