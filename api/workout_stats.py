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

def get_last_month_prop(list):
    last_month_exe = {}
    for w in list: 
        if w['workout_name'] in last_month_exe:
                last_month_exe[w['workout_name']] += 1
        else:
                last_month_exe[w['workout_name']] = 1
    #Divide by total number of workouts * 100
    last_month_exe = {k: v / len(list) * 100 for k, v in last_month_exe.items()}
    last_month_exe = {k: v for k, v in sorted(last_month_exe.items(), key=lambda item: item[1], reverse=True)}
    return last_month_exe

def get_rest_days_month(list):
    rest_day_count = 0
    for i in range(30):
        day = datetime.strptime(time(), "%d/%m/%Y %H:%M:%S EST") - timedelta(days=i)
        day = day.strftime("%d/%m/%Y")
        for d in list:
            workout = datetime.strptime(d['workout_date'], "%d/%m/%Y %H:%M:%S EST")
            workout = workout.strftime("%d/%m/%Y")
            if day == workout:
                rest_day_count += 1
    return rest_day_count
            

def get_workout_stats(user_id): 
    client = boto3.resource('dynamodb', aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key = os.getenv('AWS_SECRET_KEY'),
        region_name='ap-south-1')
    table = client.Table('w_workoutdata')
    try: 
        response = table.scan(FilterExpression = Attr('userid').eq(user_id))
        response = sorted(response['Items'], key = lambda i: i['workout_date'], reverse=True)
        within_week = get_results_within(response, 7)
        within_month = get_results_within(response, 30)
        avg_week_calories = int(sum([int(i['workout_calories_burnt']) for i in within_week])/len(within_week))
        avg_weeek_minutes = int(sum([int(i['workout_duration']) for i in within_week])/len(within_week))
        dominating_workout_week = str(max(set([i['workout_name'] for i in within_week]), key = [i['workout_duration'] for i in within_week].count))
        last_month_exe = get_last_month_prop(within_month)
        rest_days = int(get_rest_days_month(within_month))
        return 200, {'total_workouts' : len(within_week),'avg_week_calories': int(avg_week_calories), 'avg_week_minutes': avg_weeek_minutes, 'dominating_workout_week': dominating_workout_week, 'last_month_exe_prop': last_month_exe, 'rest_days': int(rest_days)}
    except Exception as e:
        return 501, str(e)

print(get_workout_stats('20852362'))