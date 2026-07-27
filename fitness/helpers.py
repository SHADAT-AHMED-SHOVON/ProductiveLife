import csv
import os
import numpy as np
from datetime import timedelta
from common.utils import ensure_data_folder, parse_date, get_today_str

FITNESS_FILE = "data/fitness.csv"

def save_workout(workout_obj):
    ensure_data_folder()
    file_exists = os.path.exists(FITNESS_FILE)
    try:
        with open(FITNESS_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["date", "exercise", "workout_type", "duration", "calories"])
            writer.writerow([workout_obj.workout_date, workout_obj.exercise, workout_obj.workout_type, workout_obj.duration, workout_obj.calories])
    except Exception as e:
        print(f"Error saving fitness record: {e}")

def save_all_workouts(records):
    """Overwrites CSV with updated workout records"""
    ensure_data_folder()
    try:
        with open(FITNESS_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["date", "exercise", "workout_type", "duration", "calories"])
            for r in records:
                writer.writerow([r["date"], r["exercise"], r["workout_type"], r["duration"], r["calories"]])
    except Exception as e:
        print(f"Error saving all fitness records: {e}")

def load_fitness():
    records = []
    if not os.path.exists(FITNESS_FILE):
        return records
    try:
        with open(FITNESS_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                records.append({
                    "date": row.get("date", get_today_str()),
                    "exercise": row["exercise"],
                    "workout_type": row["workout_type"],
                    "duration": float(row["duration"]),
                    "calories": float(row["calories"])
                })
    except Exception as e:
        print(f"Error reading fitness records: {e}")
    return records

def delete_workout_by_index(index):
    """Deletes a workout record by list index and updates CSV"""
    records = load_fitness()
    if 0 <= index < len(records):
        records.pop(index)
        save_all_workouts(records)
    return records

def calculate_stats_from_list(filtered_records):
    if not filtered_records:
        return {"total_cals": 0.0, "avg_duration": 0.0, "max_cals": 0.0}

    calories = np.array([r["calories"] for r in filtered_records])
    durations = np.array([r["duration"] for r in filtered_records])

    daily_cals = {}
    for r in filtered_records:
        d = r["date"]
        daily_cals[d] = daily_cals.get(d, 0.0) + r["calories"]
        
    max_daily_cals = float(max(daily_cals.values())) if daily_cals else 0.0

    return {
        "total_cals": float(np.sum(calories)),
        "avg_duration": float(np.mean(durations)),
        "max_cals": max_daily_cals
    }

def analyze_fitness_data(records, target_date_str=None):
    if not target_date_str:
        target_date_str = get_today_str()

    target_dt = parse_date(target_date_str)
    week_start = target_dt - timedelta(days=6)
    month_start = target_dt - timedelta(days=29)

    day_recs, week_recs, month_recs = [], [], []

    for r in records:
        r_dt = parse_date(r["date"])
        if r["date"] == target_date_str:
            day_recs.append(r)
        if week_start <= r_dt <= target_dt:
            week_recs.append(r)
        if month_start <= r_dt <= target_dt:
            month_recs.append(r)

    return {
        "day": calculate_stats_from_list(day_recs),
        "week": calculate_stats_from_list(week_recs),
        "month": calculate_stats_from_list(month_recs)
    }