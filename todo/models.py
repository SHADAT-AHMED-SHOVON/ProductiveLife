from common.utils import get_today_str

class Task:
    PRIORITY_OPTIONS = ("High", "Medium", "Low")
    STATUS_OPTIONS = ("Pending", "Done")

    def __init__(self, task_id, title, description="", priority="Medium", status="Pending", task_date=None, completed_date=""):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority if priority in self.PRIORITY_OPTIONS else "Medium"
        self.status = status if status in self.STATUS_OPTIONS else "Pending"
        self.task_date = task_date if task_date else get_today_str()
        self.completed_date = completed_date

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "date": self.task_date,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "completed_date": self.completed_date
        }