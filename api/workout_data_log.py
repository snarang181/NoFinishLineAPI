from math import fabs
from re import L
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

def user_exists(id, table):
    if id != '':
        if(table.scan(FilterExpression = Attr('email').eq(id))['Count']==0):
            return False
        else:
            return True

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
    
def get_unique_number():
    return random.randint(10000000, 99999999)

def unique_workout_id(table):
    uniqueid = get_unique_number()
    while(table.scan(FilterExpression = Attr('userid').eq(uniqueid))['Count']!=0 and table.scan(FilterExpression = Attr('workout_id').eq(uniqueid))['Count']!=0):
        uniqueid = get_unique_number()
    return uniqueid

def past_workouts(user_id):
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_workoutdata')
    if user_exists(user_id, table):
        return 401, "User does not exist"
    try: 
        response = table.scan(FilterExpression = Attr('userid').eq(user_id))
        response = sorted(response['Items'], key = lambda i: i['workout_date'], reverse=True)
        return 200, response
    except Exception as e:
        return 501, str(e)

def get_single_workout_data(user_id, workout_id):
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_workoutdata')
    if user_exists(user_id, table):
        return 401, "User does not exist"
    try:
        response = table.scan(FilterExpression = Attr('userid').eq(user_id) & Attr('workout_id').eq(workout_id))
        return 200, response['Items']
    except Exception as e:
        return 501, str(e)

def remove_workout(user_id, workout_id):
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_workoutdata')
    #remove workout from workoutdata table
    try : 
        response = table.delete_item(Key = {'userid': user_id, 'workout_id': workout_id})
        if(response['ResponseMetadata']['HTTPStatusCode']==200):
            return 200, "Workout removed"
        else : 
            return 501, "Error removing workout"
    except Exception as e:
        return 501, str(e)
        
    
def workout_log(user_id, workout_name, workout_duration, workout_calories_burnt, workout_notes):
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_workoutdata')
    if user_id == None or  workout_name == None or workout_duration == None or workout_calories_burnt == None:
        return 401, "Invalid input"
    
    if user_id == '' or  workout_name == '' or workout_duration == '' or workout_calories_burnt == '':
        return 401, "Invalid input"
    
    if user_exists(user_id, table):
        return 401, "User does not exist"
    
    try:
        response = table.put_item(
            Item = {
                'userid': str(user_id),
                'workout_id': str(unique_workout_id(table)),
                'workout_name': workout_name[0].upper() + workout_name[1:],
                'workout_duration': str(workout_duration),
                'workout_calories_burnt': str(workout_calories_burnt),
                'workout_date': time(),
                'workout_notes': str(workout_notes)
            }
        )
        if(response['ResponseMetadata']['HTTPStatusCode']==200):
            return 200, "Workout logged"
        else:
            return 402, "Workout not logged"
    except Exception as e:
        return 501, str(e)

# print(workout_log('20852362', 'Strength Training', '50', '400'))

# print(workout_log('20852362', 'Running', '30', '300'))
# print(past_workouts('20852362'))
# remove_workout('20852362', '79680243')