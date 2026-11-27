# ProductiveLife: Task & Fitness Hub

A desktop application that brings task management and fitness tracking into one place. It is built with Python and Tkinter, and stores data locally in CSV files.

## Features

### Home Dashboard
- Pick any date (2024 to 2030) and load its analytics
- Day, weekly (7 days) and monthly (30 days) summaries
- Completed and pending task counts
- Calories burned and highest daily burn, plus average workout duration (day and week)
- Auto-scaled bar chart of the selected day's completed tasks, pending tasks and calories

Pending counts include all currently pending tasks, regardless of the selected date.

### Task Manager
- Add, edit and delete tasks
- Set priority: High, Medium or Low
- Mark tasks as done, with the completion date recorded
- Filter by status and priority
- Automatic task IDs (`T-01`, `T-02`, ...), re-numbered after deletion

### Fitness Tracker
- Log workouts under Cardio, Strength or Flexibility (13 built-in exercises)
- Estimate calories from exercise type and duration, or enter them manually
- Edit and delete workout records (editing recalculates calories)
- Filter workouts by date

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| GUI | Tkinter, ttk |
| Calculations | NumPy |
| Storage | CSV files (`csv` module) |
| Dates | `datetime` module |

## Project Structure

```
ProductiveLife/
├── productivelife.py      # Entry point, navigation and dashboard
├── common/
│   └── utils.py           # Shared date and folder helpers
├── todo/
│   ├── models.py          # Task class
│   ├── helpers.py         # Task storage and analytics
│   └── views.py           # Task Manager screen
├── fitness/
│   ├── models.py          # Workout class and exercise data
│   ├── helpers.py         # Workout storage and analytics
│   └── views.py           # Fitness Tracker screen
└── data/
    ├── tasks.csv          # Created when you first save a task
    └── fitness.csv        # Created when you first log a workout
```

## Getting Started

### Prerequisites
- Python 3 with Tkinter (included in the standard Windows installer)
- NumPy

### Installation and Run

Download or clone the project, open a terminal in the project root folder, then run:

```bash
pip install numpy
python productivelife.py
```

Run the command from the root folder, because data paths are relative to it.

> **Platform note:** The app opens maximized using `state('zoomed')`, which works on Windows. On Linux this line raises an error and needs to be changed or removed.

## Data Format

**tasks.csv**

```
task_id,date,title,description,priority,status,completed_date
```

**fitness.csv**

```
date,exercise,workout_type,duration,calories
```

Dates use the `YYYY-MM-DD` format. Duration is in minutes and calories are in kcal.

## Future Improvements
- Keep manually entered calories when editing a workout
- Reject invalid dates such as 30 February instead of falling back to today
- Add weekly and monthly charts
- Move storage to SQLite
- Add unit tests
