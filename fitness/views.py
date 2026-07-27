import tkinter as tk
from tkinter import messagebox, ttk
from fitness.models import Workout
from fitness.helpers import load_fitness, save_workout, save_all_workouts, delete_workout_by_index
from common.utils import get_today_str

class FitnessFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Fitness Tracker", font=("Arial", 16, "bold"), fg="#2ECC71").pack(pady=5)

        form_frame = tk.LabelFrame(self, text="Log Workout Session", font=("Arial", 10, "bold"), padx=10, pady=5)
        form_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(form_frame, text="Date:").grid(row=0, column=0, sticky="w", pady=2)
        self.date_var = tk.StringVar(value=get_today_str())
        tk.Label(form_frame, textvariable=self.date_var, font=("Arial", 10, "bold"), fg="#2C3E50").grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(form_frame, text="Workout Type:").grid(row=1, column=0, sticky="w", pady=2)
        self.type_combo = ttk.Combobox(form_frame, values=list(Workout.EXERCISES_DATA.keys()), state="readonly", width=22)
        self.type_combo.set("Cardio")
        self.type_combo.grid(row=1, column=1, sticky="w", pady=2)
        self.type_combo.bind("<<ComboboxSelected>>", self.on_type_change)

        tk.Label(form_frame, text="Exercise:").grid(row=1, column=2, sticky="w", padx=(15, 2))
        self.ex_combo = ttk.Combobox(form_frame, state="readonly", width=22)
        self.ex_combo.grid(row=1, column=3, sticky="w", pady=2)

        tk.Label(form_frame, text="Duration (mins):").grid(row=2, column=0, sticky="w", pady=2)
        self.dur_entry = tk.Entry(form_frame, width=25)
        self.dur_entry.grid(row=2, column=1, sticky="w", pady=2)

        tk.Label(form_frame, text="Calories (kcal):").grid(row=2, column=2, sticky="w", padx=(15, 2))
        self.cal_entry = tk.Entry(form_frame, width=25)
        self.cal_entry.grid(row=2, column=3, sticky="w", pady=2)

        tk.Button(form_frame, text="Auto Calc Cal", bg="#3498DB", fg="white", font=("Arial", 8, "bold"), command=self.auto_calc_cals).grid(row=3, column=1, sticky="w", pady=5)
        tk.Button(form_frame, text="Log Workout", bg="#2ECC71", fg="white", font=("Arial", 9, "bold"), command=self.add_workout).grid(row=3, column=3, sticky="e", pady=5)

        self.on_type_change()

        cards_outer_frame = tk.LabelFrame(self, text="Logged Workouts (Card View)", font=("Arial", 10, "bold"), padx=5, pady=5)
        cards_outer_frame.pack(fill="both", expand=True, padx=15, pady=5)

        filter_frame = tk.Frame(cards_outer_frame, pady=2)
        filter_frame.pack(fill="x", padx=5, pady=(0, 5))

        tk.Label(filter_frame, text="Filter Date:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 5))
        self.date_filter_combo = ttk.Combobox(filter_frame, values=["All"], state="readonly", width=15)
        self.date_filter_combo.set("All")
        self.date_filter_combo.pack(side="left")
        self.date_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

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

    def on_type_change(self, event=None):
        w_type = self.type_combo.get()
        exercises = list(Workout.EXERCISES_DATA.get(w_type, {}).keys())
        self.ex_combo["values"] = exercises
        if exercises:
            self.ex_combo.set(exercises[0])

    def auto_calc_cals(self):
        w_type = self.type_combo.get()
        ex = self.ex_combo.get()
        try:
            dur = float(self.dur_entry.get().strip())
            rate = Workout.EXERCISES_DATA.get(w_type, {}).get(ex, 5.0)
            cals = dur * rate
            self.cal_entry.delete(0, tk.END)
            self.cal_entry.insert(0, f"{cals:.1f}")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid numeric duration!")

    def refresh_data(self):
        self.workouts = load_fitness()
        self.date_var.set(get_today_str())

        unique_dates = sorted(list(set(r["date"] for r in self.workouts)), reverse=True)
        current_selection = self.date_filter_combo.get()
        
        filter_values = ["All"] + unique_dates
        self.date_filter_combo["values"] = filter_values
        
        if current_selection not in filter_values:
            self.date_filter_combo.set("All")

        self.apply_filter()

    def apply_filter(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.workouts:
            tk.Label(self.scrollable_frame, text="No fitness sessions logged yet!", font=("Arial", 10, "italic"), fg="#7F8C8D").pack(pady=20)
            return

        selected_date = self.date_filter_combo.get()

        indexed_workouts = list(enumerate(self.workouts))
        indexed_workouts.reverse()

        if selected_date != "All":
            filtered = [(idx, rec) for idx, rec in indexed_workouts if rec["date"] == selected_date]
        else:
            filtered = indexed_workouts

        if not filtered:
            tk.Label(self.scrollable_frame, text=f"No workouts found for {selected_date}!", font=("Arial", 10, "italic"), fg="#7F8C8D").pack(pady=20)
            return

        for idx, rec in filtered:
            self.create_workout_box(idx, rec)

    def create_workout_box(self, index, rec):
        box = tk.LabelFrame(
            self.scrollable_frame,
            text=f"[{rec['date']}] {rec['exercise']} ({rec['workout_type']})",
            font=("Arial", 10, "bold"),
            bg="#E8F8F5",
            fg="#2C3E50",
            padx=10,
            pady=5,
            bd=1,
            relief="solid"
        )
        box.pack(fill="x", padx=5, pady=4)

        info_text = f"Duration: {rec['duration']} mins  |  Calories Burned: {rec['calories']} kcal"
        tk.Label(box, text=info_text, font=("Arial", 9, "bold"), bg="#E8F8F5", fg="#16A085").pack(anchor="w")

        btn_box = tk.Frame(box, bg="#E8F8F5")
        btn_box.pack(anchor="e", pady=2)

        tk.Button(
            btn_box, text="✏ Edit", font=("Arial", 8, "bold"), bg="#3498DB", fg="white", bd=0, padx=5,
            command=lambda idx=index, r=rec: self.open_edit_window(idx, r)
        ).pack(side="left", padx=2)

        tk.Button(
            btn_box, text="🗑 Delete", font=("Arial", 8, "bold"), bg="#E74C3C", fg="white", bd=0, padx=5,
            command=lambda idx=index: self.delete_workout(idx)
        ).pack(side="left", padx=2)

    def add_workout(self):
        w_type = self.type_combo.get()
        ex = self.ex_combo.get()
        dur_str = self.dur_entry.get().strip()
        cal_str = self.cal_entry.get().strip()

        if not dur_str:
            messagebox.showerror("Validation Error", "Please enter workout duration!")
            return

        try:
            dur = float(dur_str)
            if cal_str:
                cals = float(cal_str)
            else:
                rate = Workout.EXERCISES_DATA.get(w_type, {}).get(ex, 5.0)
                cals = dur * rate
        except ValueError:
            messagebox.showerror("Validation Error", "Duration and Calories must be valid numbers!")
            return

        workout = Workout(ex, w_type, dur, cals, get_today_str())
        save_workout(workout)

        messagebox.showinfo("Success", "Workout session logged successfully!")
        self.dur_entry.delete(0, tk.END)
        self.cal_entry.delete(0, tk.END)
        self.refresh_data()
        self.controller.update_home_summary()

    def open_edit_window(self, index, rec):
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Workout Session")
        edit_win.geometry("380x250")
        edit_win.resizable(False, False)
        edit_win.grab_set()

        tk.Label(edit_win, text=f"Edit Workout ({rec['date']})", font=("Arial", 11, "bold"), fg="#2C3E50").pack(pady=10)

        form = tk.Frame(edit_win, padx=15, pady=5)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Exercise:").grid(row=0, column=0, sticky="w", pady=4)
        ex_entry = tk.Entry(form, width=25)
        ex_entry.insert(0, rec['exercise'])
        ex_entry.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Type:").grid(row=1, column=0, sticky="w", pady=4)
        type_combo = ttk.Combobox(form, values=list(Workout.EXERCISES_DATA.keys()), state="readonly", width=22)
        type_combo.set(rec['workout_type'])
        type_combo.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Duration (mins):").grid(row=2, column=0, sticky="w", pady=4)
        dur_entry = tk.Entry(form, width=25)
        dur_entry.insert(0, str(rec['duration']))
        dur_entry.grid(row=2, column=1, pady=4)

        tk.Label(form, text="Calories (kcal):").grid(row=3, column=0, sticky="w", pady=4)
        cal_entry = tk.Entry(form, width=25)
        cal_entry.insert(0, str(rec['calories']))
        cal_entry.grid(row=3, column=1, pady=4)

        def save_changes():
            try:
                new_ex = ex_entry.get().strip()
                new_type = type_combo.get()
                new_dur = float(dur_entry.get().strip())

                if not new_ex:
                    messagebox.showerror("Error", "Exercise name cannot be empty!", parent=edit_win)
                    return

                rate = Workout.EXERCISES_DATA.get(new_type, {}).get(new_ex, 5.0)
                new_cal = new_dur * rate

                self.workouts[index]['exercise'] = new_ex
                self.workouts[index]['workout_type'] = new_type
                self.workouts[index]['duration'] = new_dur
                self.workouts[index]['calories'] = new_cal

                save_all_workouts(self.workouts)
                self.refresh_data()
                self.controller.update_home_summary()
                edit_win.destroy()
                messagebox.showinfo("Success", "Workout record updated successfully!")
            except ValueError:
                messagebox.showerror("Error", "Duration must be a valid number!", parent=edit_win)

        tk.Button(
            edit_win, text="Save Changes", bg="#2ECC71", fg="white", font=("Arial", 9, "bold"),
            padx=10, command=save_changes
        ).pack(pady=10)

    def delete_workout(self, index):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this workout record?"):
            delete_workout_by_index(index)
            self.refresh_data()
            self.controller.update_home_summary()