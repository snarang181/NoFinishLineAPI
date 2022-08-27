from flask import Flask, request, render_template
from flask_cors import CORS
from flask_mail import Mail, Message
import os, requests, json

app = Flask(__name__)
api_key = 'aac48d6f-b63d-47a8-ada0-731db9955679'

@app.route('/', methods=['POST'])
def home():
    data = request.get_json()
    print(data)
    try:
        if(data['auth_key'] != api_key):
            return {"message": "Invalid API Key",}, 401
    except:
        return {"message": "API key required",}, 401
    return {"message": "Hello World!"}

