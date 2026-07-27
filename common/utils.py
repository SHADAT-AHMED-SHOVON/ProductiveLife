import os
from datetime import date, datetime

def ensure_data_folder():
    if not os.path.exists("data"):
        os.makedirs("data")

def get_today_str():
    return date.today().strftime("%Y-%m-%d")

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return date.today()