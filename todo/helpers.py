import csv
import os
from datetime import timedelta
from common.utils import ensure_data_folder, get_today_str, parse_date
from todo.models import Task

TASKS_FILE = "data/tasks.csv"

def save_tasks(task_list):
    ensure_data_folder()
    try:
        with open(TASKS_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["task_id", "date", "title", "description", "priority", "status", "completed_date"])
            for task in task_list:
                writer.writerow([task.task_id, task.task_date, task.title, task.description, task.priority, task.status, task.completed_date])
    except Exception as e:
        print(f"Error saving tasks: {e}")

def load_tasks():
    ensure_data_folder()
    task_list = []
    
    if not os.path.exists(TASKS_FILE):
        return task_list

    try:
        with open(TASKS_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                task = Task(
                    row["task_id"], 
                    row["title"], 
                    row.get("description", ""), 
                    row["priority"], 
                    row["status"],
                    row.get("date", get_today_str()),
                    row.get("completed_date", "")
                )
                task_list.append(task)
    except Exception as e:
        print(f"Error loading tasks: {e}")

    return task_list

def reindex_tasks(task_list):
    for idx, task in enumerate(task_list, start=1):
        task.task_id = f"T-{idx:02d}"
    return task_list

def generate_next_task_id(task_list):
    next_num = len(task_list) + 1
    return f"T-{next_num:02d}"

def delete_task_by_id(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t.task_id != task_id]
    tasks = reindex_tasks(tasks)
    save_tasks(tasks)
    return tasks

def analyze_task_data(tasks, target_date_str=None):
    if not target_date_str:
        target_date_str = get_today_str()

    target_dt = parse_date(target_date_str)
    week_start = target_dt - timedelta(days=6)
    month_start = target_dt - timedelta(days=29)

    def filter_counts(t_list, window_type="day"):
        pending = sum(1 for t in t_list if t.status == "Pending")
        
        if window_type == "day":
            done = sum(1 for t in t_list if t.status == "Done" and t.completed_date == target_date_str)
        elif window_type == "week":
            done = sum(1 for t in t_list if t.status == "Done" and t.completed_date and week_start <= parse_date(t.completed_date) <= target_dt)
        else:
            done = sum(1 for t in t_list if t.status == "Done" and t.completed_date and month_start <= parse_date(t.completed_date) <= target_dt)
            
        total = done + pending
        return {"done": done, "pending": pending, "total": total}

    return {
        "day": filter_counts(tasks, "day"),
        "week": filter_counts(tasks, "week"),
        "month": filter_counts(tasks, "month")
    }