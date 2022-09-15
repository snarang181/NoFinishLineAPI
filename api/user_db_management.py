from math import fabs
from urllib import response
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import pytz
from passlib.hash import pbkdf2_sha256
import random
from dotenv import load_dotenv
import os, requests, json, string

load_dotenv()

def time():
    timeZ_Ny = pytz.timezone('America/New_York')
    now = datetime.now(timeZ_Ny)
    return now.strftime("%d/%m/%Y %H:%M:%S EST")

def decrypt_password(password,salt,hash):
    return pbkdf2_sha256.verify(password+salt, hash)

def encrypt_password(password,salt):
    return pbkdf2_sha256.hash(password+salt)

def get_unique_number():
    return random.randint(10000000, 99999999)

def unqiue_id(table):
    uniqueid = get_unique_number()
    while(table.scan(FilterExpression = Attr('userid').eq(uniqueid))['Count']!=0):
        uniqueid = get_unique_number()
    return uniqueid

def user_exists(id, table):
    if id != '':
        if(table.scan(FilterExpression = Attr('email').eq(id))['Count']==0):
            return False
        else:
            return True

def user_register(id, password,first_name, last_name, age, weight):
    if (id == None or password == None) or (id == '' or password == ''):
        return 401, "Invalid input", None, None
    
    if '@' not in id:
        return 401, "Invalid input", None, None
    
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_userdata')
    if user_exists(id, table):
        return 401, "User already exists", None, None
    else:
        auth_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        unique_identification = str(unqiue_id(table))
        temp_id = str(abs(random.randint(1, 1000) - random.randint(2000, 10000)))
        response = table.put_item(
            Item = {
                'userid': unique_identification,
                'email': id,
                'password': encrypt_password(password,temp_id),
                'first_name': first_name,
                'last_name': last_name,
                'age': age,
                'weight': weight,
                'registration_datetime': time(),
                'last_signin_datetime': time(),
                'auth_token': [auth_token],
                'one_signal_ids': []
            }
        )
        if(response['ResponseMetadata']['HTTPStatusCode']==200):
            message = 'Welcome!'
            return 202, "User registered successfully", auth_token, unique_identification
        else :
            return 501, response, None, None
    
def check_user_exists(id):
    if id.find('@') == -1:
        return 403, "Invalid Input"
    
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_userdata')
    try: 
        res = table.scan(FilterExpression = Attr('email').eq(id))
        if res['Count'] == 0:
            return 201, "User does not exist"
        else:
            return 202, "User exists"
    except Exception as e:
        return 501, str(e)
    
    
            
    

        
        
    