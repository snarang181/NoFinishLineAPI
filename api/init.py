from flask import Flask, request, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
import os, requests, json
from dotenv import load_dotenv
from  api.user_db_management import user_register,check_user_exists


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
    status_code, message, auth_token, userid  = user_register(id, password)
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


    





