from math import fabs
from tabnanny import check
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
                'email': id.lower(),
                'password': encrypt_password(str(password),str(unique_identification)),
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

def verify_password(id,password,table):
    res = table.scan(FilterExpression = Attr('email').eq(id))
    return decrypt_password(password, res['Items'][0]['userid'], res['Items'][0]['password']), res['Items'][0]['userid'] 


def user_login(id, password):
    email = 'EMPTY'
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_userdata')
    if(not user_exists(id,table)):
        return 403, "User does not exist", None, None
    flag, userid = verify_password(id,password,table)
    if flag: 
        auth_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        response = table.update_item(
                Key={
                    'userid': userid
                },
                UpdateExpression="set last_signin_datetime = :val1, auth_token = list_append(auth_token, :val2)",
                 ExpressionAttributeValues={
                    ':val1': time(),
                    ':val2': [auth_token]
                },
                ReturnValues="UPDATED_NEW"
                )
        return 200, "Successfully logged in", auth_token, userid
    else: 
        return 401, "Invalid password", None, None

    
def verify_auth_token(id, token):
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_userdata')
    res = table.scan(FilterExpression = Attr('userid').eq(str(id)))
    if(res['Count']==0):
        return 403, "User does not exist"
    else:
        if(token in res['Items'][0]['auth_token']):
            return 200, "Token verified"
        else:
            return 401, "Invalid token"
        
    
    
    
            
    

        
        
    