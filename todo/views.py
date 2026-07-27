import tkinter as tk
from tkinter import messagebox, ttk
from todo.models import Task
from todo.helpers import load_tasks, save_tasks, generate_next_task_id, delete_task_by_id
from common.utils import get_today_str

class TaskFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Task Manager", font=("Arial", 16, "bold"), fg="#3498DB").pack(pady=5)

        form_frame = tk.LabelFrame(self, text="Add New Task", font=("Arial", 10, "bold"), padx=10, pady=5)
        form_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(form_frame, text="Task ID:").grid(row=0, column=0, sticky="w", pady=2)
        self.id_var = tk.StringVar()
        tk.Label(form_frame, textvariable=self.id_var, font=("Arial", 10, "bold"), fg="#8E44AD").grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(form_frame, text="Date:").grid(row=0, column=2, sticky="w", padx=(15, 2))
        self.date_var = tk.StringVar(value=get_today_str())
        tk.Label(form_frame, textvariable=self.date_var, font=("Arial", 10, "bold"), fg="#2C3E50").grid(row=0, column=3, sticky="w")

        tk.Label(form_frame, text="Title:").grid(row=1, column=0, sticky="w", pady=2)
        self.title_entry = tk.Entry(form_frame, width=30)
        self.title_entry.grid(row=1, column=1, columnspan=3, sticky="w", pady=2)

        tk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky="w", pady=2)
        self.desc_entry = tk.Entry(form_frame, width=30)
        self.desc_entry.grid(row=2, column=1, columnspan=3, sticky="w", pady=2)

        tk.Label(form_frame, text="Priority:").grid(row=3, column=0, sticky="w", pady=2)
        self.priority_combo = ttk.Combobox(form_frame, values=Task.PRIORITY_OPTIONS, state="readonly", width=27)
        self.priority_combo.set("Medium")
        self.priority_combo.grid(row=3, column=1, columnspan=3, sticky="w", pady=2)

        tk.Button(form_frame, text="Add Task", bg="#2ECC71", fg="white", font=("Arial", 9, "bold"), command=self.add_task).grid(row=4, column=3, sticky="e", pady=5)

        cards_outer_frame = tk.LabelFrame(self, text="Task List (Card View)", font=("Arial", 10, "bold"), padx=5, pady=5)
        cards_outer_frame.pack(fill="both", expand=True, padx=15, pady=5)

        filter_frame = tk.Frame(cards_outer_frame, pady=2)
        filter_frame.pack(fill="x", padx=5, pady=(0, 5))

        tk.Label(filter_frame, text="Status:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 5))
        self.filter_combo = ttk.Combobox(filter_frame, values=["All", "Done", "Pending"], state="readonly", width=10)
        self.filter_combo.set("All")
        self.filter_combo.pack(side="left", padx=(0, 15))
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        tk.Label(filter_frame, text="Priority:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 5))
        self.priority_filter_combo = ttk.Combobox(filter_frame, values=["All"] + list(Task.PRIORITY_OPTIONS), state="readonly", width=10)
        self.priority_filter_combo.set("All")
        self.priority_filter_combo.pack(side="left")
        self.priority_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        self.canvas = tk.Canvas(cards_outer_frame, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(cards_outer_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def refresh_data(self):
        self.tasks = load_tasks()
        self.id_var.set(generate_next_task_id(self.tasks))
        self.date_var.set(get_today_str())

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.tasks:
            tk.Label(self.scrollable_frame, text="No tasks added yet!", font=("Arial", 10, "italic"), fg="#7F8C8D").pack(pady=20)
            return

        displayed_tasks = list(reversed(self.tasks))

        selected_status = self.filter_combo.get()
        if selected_status != "All":
            displayed_tasks = [t for t in displayed_tasks if t.status == selected_status]

        selected_priority = self.priority_filter_combo.get()
        if selected_priority != "All":
            displayed_tasks = [t for t in displayed_tasks if t.priority == selected_priority]

        if not displayed_tasks:
            tk.Label(self.scrollable_frame, text="No matching tasks found!", font=("Arial", 10, "italic"), fg="#7F8C8D").pack(pady=20)
            return

        for t in displayed_tasks:
            self.create_task_box(t)

    def create_task_box(self, task):
        status_colors = {"Pending": "#FFF9E6", "Done": "#E8F8F5"}
        status_border = {"Pending": "#F1C40F", "Done": "#2ECC71"}

        box = tk.LabelFrame(
            self.scrollable_frame,
            text=f"[{task.task_id}] {task.title} (Created: {task.task_date})",
            font=("Arial", 10, "bold"),
            bg=status_colors.get(task.status, "white"),
            fg="#2C3E50",
            padx=10,
            pady=5,
            bd=1,
            relief="solid"
        )
        box.pack(fill="x", padx=5, pady=4)

        info_text = f"Priority: {task.priority}  |  Status: {task.status}"
        if task.status == "Done" and task.completed_date:
            info_text += f"  |  Completed: {task.completed_date}"

        tk.Label(
            box, 
            text=info_text, 
            font=("Arial", 9, "bold"), 
            bg=status_colors.get(task.status, "white"), 
            fg=status_border.get(task.status, "black")
        ).pack(anchor="w")

        if task.description:
            tk.Label(
                box, 
                text=f"Desc: {task.description}", 
                font=("Arial", 9), 
                bg=status_colors.get(task.status, "white"), 
                fg="#34495E"
            ).pack(anchor="w", pady=2)

        btn_box = tk.Frame(box, bg=status_colors.get(task.status, "white"))
        btn_box.pack(anchor="e", pady=2)

        if task.status != "Done":
            tk.Button(
                btn_box, text="✔ Done", font=("Arial", 8, "bold"), bg="#2ECC71", fg="white", bd=0, padx=5,
                command=lambda tid=task.task_id: self.change_status(tid, "Done")
            ).pack(side="left", padx=2)

        tk.Button(
            btn_box, text="✏ Edit", font=("Arial", 8, "bold"), bg="#3498DB", fg="white", bd=0, padx=5,
            command=lambda t=task: self.open_edit_window(t)
        ).pack(side="left", padx=2)

        tk.Button(
            btn_box, text="🗑 Delete", font=("Arial", 8, "bold"), bg="#E74C3C", fg="white", bd=0, padx=5,
            command=lambda tid=task.task_id: self.delete_task(tid)
        ).pack(side="left", padx=2)

    def add_task(self):
        title = self.title_entry.get().strip()
        desc = self.desc_entry.get().strip()
        priority = self.priority_combo.get()

        if not title:
            messagebox.showerror("Validation Error", "Task Title cannot be empty!")
            return

        new_id = self.id_var.get()
        new_task = Task(new_id, title, desc, priority, "Pending", get_today_str(), "")
        self.tasks.append(new_task)
        save_tasks(self.tasks)

        messagebox.showinfo("Success", f"Task {new_id} Added for {get_today_str()}!")
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.refresh_data()
        self.controller.update_home_summary()

    def open_edit_window(self, task):
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Edit Task [{task.task_id}]")
        edit_win.geometry("360x240")
        edit_win.resizable(False, False)
        edit_win.grab_set()

        tk.Label(edit_win, text=f"Edit Task Details ({task.task_id})", font=("Arial", 11, "bold"), fg="#2C3E50").pack(pady=10)

        form = tk.Frame(edit_win, padx=15, pady=5)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Title:").grid(row=0, column=0, sticky="w", pady=4)
        title_entry = tk.Entry(form, width=28)
        title_entry.insert(0, task.title)
        title_entry.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Description:").grid(row=1, column=0, sticky="w", pady=4)
        desc_entry = tk.Entry(form, width=28)
        desc_entry.insert(0, task.description)
        desc_entry.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Priority:").grid(row=2, column=0, sticky="w", pady=4)
        priority_combo = ttk.Combobox(form, values=Task.PRIORITY_OPTIONS, state="readonly", width=25)
        priority_combo.set(task.priority)
        priority_combo.grid(row=2, column=1, pady=4)

        def save_changes():
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showerror("Error", "Title cannot be empty!", parent=edit_win)
                return

            task.title = new_title
            task.description = desc_entry.get().strip()
            task.priority = priority_combo.get()

            save_tasks(self.tasks)
            self.refresh_data()
            self.controller.update_home_summary()
            edit_win.destroy()
            messagebox.showinfo("Success", f"Task {task.task_id} updated successfully!")

        tk.Button(
            edit_win, text="Save Changes", bg="#2ECC71", fg="white", font=("Arial", 9, "bold"), 
            padx=10, command=save_changes
        ).pack(pady=10)

    def change_status(self, task_id, new_status):
        for t in self.tasks:
            if t.task_id == task_id:
                t.status = new_status
                if new_status == "Done":
                    t.completed_date = get_today_str()
                else:
                    t.completed_date = ""
                break
        save_tasks(self.tasks)
        self.refresh_data()
        self.controller.update_home_summary()

    def delete_task(self, task_id):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task {task_id}?"):
            delete_task_by_id(task_id)
            self.refresh_data()
            self.controller.update_home_summary()