from flask import Flask, request, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
import os, requests, json
from dotenv import load_dotenv
from api.user_db_management import user_register

load_dotenv()

app = Flask(__name__)
api_key = os.environ.get('API_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')



@app.route('/', methods=['GET'])
def landing():
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
    status_code, message, auth_token, userid  = user_register(id, password)
    return {"message": data, "auth_token": auth_token, "userID":str(userid)}, status_code

    
    # return user_register(data['email'], data['password'])






