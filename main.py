import os
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

DATABASE_FILE = "weight_tracker.db"
DATE_FORMAT = "%Y-%m-%d"


def create_date_entry(parent):
    date_entry = tk.Entry(parent)
    today_date = datetime.now().strftime("%Y-%m-%d")
    date_entry.insert(0, today_date)
    return date_entry


def setup_gui():
    root = tk.Tk()
    root.title("Weight Tracker")
    root.geometry("500x450")

    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    create_label(input_frame, "Enter Weight (lbs):", 0, 0)
    weight_entry = create_entry(input_frame, 0, 1)

    create_label(input_frame, "Enter Date (YYYY-MM-DD):", 1, 0)
    date_entry = create_date_entry(input_frame)
    date_entry.grid(row=1, column=1, padx=10, pady=5)

    log_button = tk.Button(
        input_frame,
        text="Log Weight",
        command=lambda: log_specific_date(
            date_entry, weight_entry, table_frame, moving_avg_label
        ),
    )
    log_button.grid(row=2, column=0, columnspan=2, pady=5)

    display_frame = tk.Frame(root)
    display_frame.pack(pady=5)

    tk.Label(
        display_frame, text="Last 10 Weigh-Ins:", font=("Helvetica", 12, "bold")
    ).pack()

    table_frame = tk.Frame(display_frame)
    table_frame.pack(pady=(5, 0))

    moving_avg_label = tk.Label(
        display_frame,
        text="Moving Average: ",
        font=("Helvetica", 14, "bold"),
        fg="blue",
    )
    moving_avg_label.pack(pady=(10, 0))

    update_display(table_frame, moving_avg_label)

    root.mainloop()


def create_label(parent, text, row, column, **kwargs):
    label = tk.Label(parent, text=text, **kwargs)
    label.grid(row=row, column=column, padx=10, pady=10)
    return label


def create_entry(parent, row, column):
    entry = tk.Entry(parent)
    entry.grid(row=row, column=column, padx=10, pady=10)
    return entry


def update_display(table_frame, moving_avg_label):
    for widget in table_frame.winfo_children():
        widget.destroy()

    entries = get_last_10_entries()

    if entries:
        total_weight = 0

        header_frame = tk.Frame(table_frame)
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame, text="Date", borderwidth=1, relief="solid", width=15
        ).pack(side=tk.LEFT)
        tk.Label(
            header_frame, text="Weight (lbs)", borderwidth=1, relief="solid", width=15
        ).pack(side=tk.LEFT)
        tk.Label(
            header_frame, text="Difference", borderwidth=1, relief="solid", width=15
        ).pack(side=tk.LEFT)

        for date, weight, diff in entries:
            row_frame = tk.Frame(table_frame)
            row_frame.pack(fill=tk.X)
            tk.Label(
                row_frame, text=date, borderwidth=1, relief="solid", width=15
            ).pack(side=tk.LEFT)
            tk.Label(
                row_frame, text=f"{weight:.1f}", borderwidth=1, relief="solid", width=15
            ).pack(side=tk.LEFT)
            tk.Label(
                row_frame, text=diff, borderwidth=1, relief="solid", width=15
            ).pack(side=tk.LEFT)
            total_weight += weight

        moving_avg = total_weight / len(entries)
        moving_avg_label.config(text=f"Moving Average: {moving_avg:.1f} lbs")
    else:
        tk.Label(table_frame, text="No weigh-ins recorded yet.", width=45).pack()
        moving_avg_label.config(text="Moving Average: N/A")


def log_specific_date(date_entry, weight_entry, table_frame, moving_avg_label):
    try:
        purge_records(DATABASE_FILE, years=10)
        date_str = date_entry.get()
        weight = float(weight_entry.get())
        validate_weight(weight)
        date = validate_date(date_str)

        insert_or_update_weigh_in(date, weight)
        messagebox.showinfo("Success", f"Weigh-in for {date} logged successfully!")
        reset_entries(date_entry, weight_entry)

    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Error: {e}")
        weight_entry.delete(0, tk.END)
    except IndexError:
        messagebox.showerror(
            "Invalid Input", "Please enter the date in YYYY-MM-DD format."
        )
    update_display(table_frame, moving_avg_label)


def validate_weight(weight):
    if weight <= 0:
        raise ValueError("Weight must be greater than zero.")


def validate_date(date_str):
    date = datetime.strptime(date_str.strip(), DATE_FORMAT).strftime(DATE_FORMAT)
    if datetime.strptime(date, DATE_FORMAT) > datetime.now():
        raise ValueError("Date cannot be in the future.")
    return date


def reset_entries(date_entry, weight_entry):
    weight_entry.delete(0, tk.END)
    today_date = datetime.now().strftime(DATE_FORMAT)
    date_entry.delete(0, tk.END)
    date_entry.insert(0, today_date)


def setup_database():
    if not os.path.exists(DATABASE_FILE):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS weigh_ins (
                date TEXT PRIMARY KEY,
                weight REAL
            )
            """
        )
        conn.commit()
        conn.close()


def purge_records(db_file, years=None):
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            if years:
                cursor.execute(
                    "DELETE FROM weigh_ins WHERE date < date('now', ?)",
                    (f"-{years} years",),
                )
            else:
                cursor.execute("DELETE FROM weigh_ins")
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def fetch_last_entries(limit=10):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date, weight FROM weigh_ins ORDER BY date DESC LIMIT ?",
                (limit,),
            )
            entries = cursor.fetchall()
        return entries[::-1]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []


def calculate_differences(entries):
    previous_weight = None
    differences = []
    for entry in entries:
        date, weight = entry
        if previous_weight is None:
            difference = "-"
        else:
            difference = (
                f"{weight - previous_weight:.1f} lbs"
                if weight - previous_weight != 0
                else "-"
            )
        differences.append((date, weight, difference))
        previous_weight = weight
    return differences


def get_last_10_entries():
    entries = fetch_last_entries()
    if not entries:
        return []
    return calculate_differences(entries)


def insert_or_update_weigh_in(date, weight):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM weigh_ins WHERE date = ?", (date,))
            result = cursor.fetchone()
            if result:
                cursor.execute(
                    "UPDATE weigh_ins SET weight = ? WHERE date = ?", (weight, date)
                )
            else:
                cursor.execute(
                    "INSERT INTO weigh_ins (date, weight) VALUES (?, ?)", (date, weight)
                )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")


if __name__ == "__main__":
    setup_database()
    setup_gui()
