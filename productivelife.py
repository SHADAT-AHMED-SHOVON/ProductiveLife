import os
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from common.utils import get_today_str
from todo.views import TaskFrame
from todo.helpers import load_tasks, analyze_task_data

from fitness.views import FitnessFrame
from fitness.helpers import load_fitness, analyze_fitness_data

class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="ProductiveLife Dashboard", font=("Arial", 16, "bold"), fg="#2C3E50").pack(pady=10)

        date_bar = tk.Frame(self, bg="#ECF0F1", padx=10, pady=8)
        date_bar.pack(fill="x", padx=15, pady=5)

        tk.Label(date_bar, text="Select Analytics Date:", font=("Arial", 10, "bold"), bg="#ECF0F1").pack(side="left", padx=5)

        today_dt = datetime.now()

        self.year_combo = ttk.Combobox(date_bar, values=[str(y) for y in range(2024, 2031)], state="readonly", width=6)
        self.year_combo.set(today_dt.strftime("%Y"))
        self.year_combo.pack(side="left", padx=3)

        self.month_combo = ttk.Combobox(date_bar, values=[f"{m:02d}" for m in range(1, 13)], state="readonly", width=4)
        self.month_combo.set(today_dt.strftime("%m"))
        self.month_combo.pack(side="left", padx=3)

        self.day_combo = ttk.Combobox(date_bar, values=[f"{d:02d}" for d in range(1, 32)], state="readonly", width=4)
        self.day_combo.set(today_dt.strftime("%d"))
        self.day_combo.pack(side="left", padx=3)

        tk.Button(date_bar, text="Load Analytics", bg="#3498DB", fg="white", font=("Arial", 9, "bold"), command=self.refresh_home).pack(side="left", padx=10)
        tk.Button(date_bar, text="Set Today", bg="#2ECC71", fg="white", font=("Arial", 9, "bold"), command=self.set_today_and_refresh).pack(side="left", padx=2)

        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[10, 2])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="x", padx=15, pady=10)

        self.day_tab = tk.Frame(self.notebook, padx=15, pady=10)
        self.week_tab = tk.Frame(self.notebook, padx=15, pady=10)
        self.month_tab = tk.Frame(self.notebook, padx=15, pady=10)

        self.notebook.add(self.day_tab, text=" Day Analytics ")
        self.notebook.add(self.week_tab, text=" Weekly (7 Days) ")
        self.notebook.add(self.month_tab, text=" Monthly (30 Days) ")

        self.day_label = tk.Label(self.day_tab, text="", font=("Arial", 11), justify="left", anchor="nw")
        self.day_label.pack(fill="both", expand=True)

        self.week_label = tk.Label(self.week_tab, text="", font=("Arial", 11), justify="left", anchor="nw")
        self.week_label.pack(fill="both", expand=True)

        self.month_label = tk.Label(self.month_tab, text="", font=("Arial", 11), justify="left", anchor="nw")
        self.month_label.pack(fill="both", expand=True)

        canvas_box = tk.LabelFrame(self, text="Day Metrics Diagram (Auto Scaled)", font=("Arial", 10, "bold"), padx=5, pady=5)
        canvas_box.pack(fill="both", expand=True, padx=15, pady=5)

        self.canvas = tk.Canvas(canvas_box, bg="white", height=200)
        self.canvas.pack(fill="both", expand=True, pady=5)

    def set_today_and_refresh(self):
        today_dt = datetime.now()
        self.year_combo.set(today_dt.strftime("%Y"))
        self.month_combo.set(today_dt.strftime("%m"))
        self.day_combo.set(today_dt.strftime("%d"))
        self.refresh_home()

    def refresh_home(self):
        selected_date = f"{self.year_combo.get()}-{self.month_combo.get()}-{self.day_combo.get()}"

        try:
            tasks = load_tasks()
            fitness_recs = load_fitness()
            
            task_analytics = analyze_task_data(tasks, selected_date)
            fit_analytics = analyze_fitness_data(fitness_recs, selected_date)

            t_day = task_analytics["day"]
            f_day = fit_analytics["day"]

            txt_day = (
                f"📅 Target Date: {selected_date}\n\n"
                f"[ Task Summary ]\n"
                f"• Completed Tasks:  {t_day['done']}\n"
                f"• Pending Tasks:    {t_day['pending']}\n"
                f"• Total Logged:     {t_day['total']}\n\n"
                f"[ Fitness Summary ]\n"
                f"• Total Calories:   {f_day['total_cals']:.1f} kcal\n"
                f"• Average Duration: {f_day['avg_duration']:.1f} mins\n"
                f"• Highest Daily Burn: {f_day['max_cals']:.1f} kcal"
            )
            self.day_label.config(text=txt_day)

            t_wk = task_analytics["week"]
            f_wk = fit_analytics["week"]
            txt_wk = (
                f"📊 7-Day Window Ending: {selected_date}\n\n"
                f"• Tasks Completed:  {t_wk['done']} / {t_wk['total']} total\n"
                f"• Total Burned:     {f_wk['total_cals']:.1f} kcal\n"
                f"• Highest Daily Burn: {f_wk['max_cals']:.1f} kcal\n"
                f"• Daily Avg Session:{f_wk['avg_duration']:.1f} mins"
            )
            self.week_label.config(text=txt_wk)

            t_mth = task_analytics["month"]
            f_mth = fit_analytics["month"]
            txt_mth = (
                f"📈 30-Day Window Ending: {selected_date}\n\n"
                f"• Tasks Completed:  {t_mth['done']} / {t_mth['total']} total\n"
                f"• Total Burned:     {f_mth['total_cals']:.1f} kcal\n"
                f"• Highest Daily Burn: {f_mth['max_cals']:.1f} kcal"
            )
            self.month_label.config(text=txt_mth)

            self.draw_diagram(t_day['done'], t_day['pending'], f_day['total_cals'])

        except Exception as e:
            messagebox.showerror("Data Error", f"Failed to load analytics: {str(e)}")

    def draw_diagram(self, done_tasks, pending_tasks, cals):
        self.canvas.delete("all")
        self.update_idletasks()
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 100: width = 600
        if height < 100: height = 200

        if done_tasks == 0 and pending_tasks == 0 and cals == 0:
            self.canvas.create_text(width/2, height/2, text="No data available for selected date.", font=("Arial", 12, "italic"), fill="gray")
            return

        y_bottom = height - 30
        y_top = 30
        max_bar_height = y_bottom - y_top

        max_task_val = max(done_tasks, pending_tasks)
        task_scale = max_task_val if max_task_val > 0 else 1
        cal_scale = cals if cals > 0 else 1

        data = [
            ("Done Tasks", done_tasks, task_scale, "#2ECC71"),
            ("Pending Tasks", pending_tasks, task_scale, "#E74C3C"),
            ("Calories Burned", cals, cal_scale, "#3498DB")
        ]

        bar_w = 90
        gap = 50
        start_x = (width - (3 * bar_w + 2 * gap)) / 2

        self.canvas.create_line(20, y_bottom, width - 20, y_bottom, fill="#7F8C8D", width=2)

        for i, (label, val, scale, color) in enumerate(data):
            x0 = start_x + i * (bar_w + gap)
            x1 = x0 + bar_w
            
            bar_h = (val / scale) * max_bar_height if scale > 0 else 0
            
            if val > 0 and bar_h < 5: 
                bar_h = 5
                
            y0 = y_bottom - bar_h

            if val > 0:
                self.canvas.create_rectangle(x0, y0, x1, y_bottom, fill=color, outline="black")
                display_val = f"{val:.1f}" if isinstance(val, float) else str(val)
                self.canvas.create_text((x0+x1)/2, y0 - 12, text=display_val, font=("Arial", 10, "bold"))
            
            self.canvas.create_text((x0+x1)/2, y_bottom + 15, text=label, font=("Arial", 9, "bold"))

class ProductiveLifeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ProductiveLife: Task & Fitness Hub")
        self.state('zoomed')

        nav_bar = tk.Frame(self, bg="#2C3E50", height=45)
        nav_bar.pack(side="top", fill="x")

        tk.Button(nav_bar, text="🏠 Home Dashboard", bg="#3498DB", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5, command=self.show_home).pack(side="left", padx=5, pady=5)
        tk.Button(nav_bar, text="📋 Task Manager", bg="#2ECC71", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5, command=lambda: self.show_frame("TaskFrame")).pack(side="left", padx=5, pady=5)
        tk.Button(nav_bar, text="💪 Fitness Tracker", bg="#E67E22", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=10, pady=5, command=lambda: self.show_frame("FitnessFrame")).pack(side="left", padx=5, pady=5)

        self.container = tk.Frame(self)
        self.container.pack(side="bottom", fill="both", expand=True)

        self.frames = {}
        for F in (HomeFrame, TaskFrame, FitnessFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_home()

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        if hasattr(frame, "refresh_data"):
            frame.refresh_data()
        elif hasattr(frame, "refresh_home"):
            frame.refresh_home()
        frame.tkraise()

    def show_home(self):
        self.frames["HomeFrame"].refresh_home()
        self.frames["HomeFrame"].tkraise()

    def update_home_summary(self):
        self.frames["HomeFrame"].refresh_home()

if __name__ == "__main__":
    app = ProductiveLifeApp()
    app.mainloop()