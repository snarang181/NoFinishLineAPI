from math import fabs
from re import L
from urllib import response
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta
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

def get_results_within(list, days):
    today = time()
    time_diff = datetime.strptime(today, "%d/%m/%Y %H:%M:%S EST") - timedelta(days=days)
    filtered = [i for i in list if datetime.strptime(i['workout_date'], "%d/%m/%Y %H:%M:%S EST") > time_diff]
    return filtered

#Total Calories burned in seven days and avg over 30 days 
def calorie_stats(user_id): 
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_workoutdata')
    try: 
        response = table.scan(FilterExpression = Attr('userid').eq(user_id))
        response = sorted(response['Items'], key = lambda i: i['workout_date'], reverse=True)
        within_week = get_results_within(response, 7)
        within_month = get_results_within(response, 30)
        
        return 200, response
    except Exception as e:
        return 501, str(e)

print(calorie_stats('20852362'))