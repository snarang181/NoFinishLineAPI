import json

def load_all_workouts():
    with open('all_exercises.json') as f:
        return json.load(f)
    
def get_workout_data(workout_name):
    all_workouts = load_all_workouts()
    for workout in all_workouts:
        if workout['name'] == workout_name:
            data = {}
            data['name'] = workout['name'].title()
            data['level'] = workout['level'].title()
            muscle_groups = ''
            for m in workout['primaryMuscles']:
                muscle_groups += m.title() + ', '
            for s in workout['secondaryMuscles']:
                muscle_groups += s.title() + ', '
            data['Muscle Groups'] = muscle_groups.trim()
            data['category'] = workout['category'].title()
            instructions = ''
            for i in workout['instructions']:
                instructions += i + ' '
            data['instructions'] = instructions.trim()
            return 200, data
    return 404, "Workout not found"

def send_data(workout_name):
    code, workout_data = get_workout_data(workout_name)
    if code == 404: 
        return 404, "Workout not found"
    return 200, workout_data
