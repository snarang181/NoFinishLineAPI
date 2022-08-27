from flask import Flask, request, render_template
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World!"