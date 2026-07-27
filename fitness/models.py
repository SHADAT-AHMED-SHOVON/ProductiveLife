from common.utils import get_today_str

class Workout:
    EXERCISES_DATA = {
        "Cardio": {
            "Running": 10.5,
            "Cycling": 8.0,
            "Swimming": 9.5,
            "Walking": 4.0,
            "Jumping Rope": 12.0,
            "HIIT": 11.0,
            "Rowing": 8.5
        },
        "Strength": {
            "Squats": 7.0,
            "Bench Press": 6.0,
            "Deadlifts": 8.0,
            "Push-ups": 5.0
        },
        "Flexibility": {
            "Yoga": 3.5,
            "Stretching": 2.5
        }
    }

    def __init__(self, exercise, workout_type="Cardio", duration=0.0, calories=0.0, workout_date=None):
        self.exercise = exercise
        self.workout_type = workout_type
        self.duration = float(duration)
        self.calories = float(calories)
        self.workout_date = workout_date if workout_date else get_today_str()