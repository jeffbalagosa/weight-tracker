import os
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

DATABASE_FILE = "weight_tracker.db"


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

    weight_label = tk.Label(input_frame, text="Enter Weight (lbs):")
    weight_label.grid(row=0, column=0, padx=10, pady=10)
    weight_entry = tk.Entry(input_frame)
    weight_entry.grid(row=0, column=1, padx=10, pady=10)

    specific_date_label = tk.Label(input_frame, text="Enter Date (YYYY-MM-DD):")
    specific_date_label.grid(row=1, column=0, padx=10, pady=5)

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

    display_label = tk.Label(
        display_frame, text="Last 10 Weigh-Ins:", font=("Helvetica", 12, "bold")
    )
    display_label.pack()

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


def update_display(table_frame, moving_avg_label):
    for widget in table_frame.winfo_children():
        widget.destroy()

    entries = get_last_10_entries()

    if entries:
        total_weight = 0

        tk.Label(
            table_frame, text="Date", borderwidth=1, relief="solid", width=15
        ).grid(row=0, column=0)
        tk.Label(
            table_frame, text="Weight (lbs)", borderwidth=1, relief="solid", width=15
        ).grid(row=0, column=1)
        tk.Label(
            table_frame, text="Difference", borderwidth=1, relief="solid", width=15
        ).grid(row=0, column=2)

        for i, (date, weight, diff) in enumerate(entries, start=1):
            tk.Label(
                table_frame, text=date, borderwidth=1, relief="solid", width=15
            ).grid(row=i, column=0)
            tk.Label(
                table_frame,
                text=f"{weight:.1f}",
                borderwidth=1,
                relief="solid",
                width=15,
            ).grid(row=i, column=1)
            tk.Label(
                table_frame, text=diff, borderwidth=1, relief="solid", width=15
            ).grid(row=i, column=2)
            total_weight += weight

        moving_avg = total_weight / len(entries)
        moving_avg_label.config(text=f"Moving Average: {moving_avg:.2f} lbs")
    else:
        tk.Label(table_frame, text="No weigh-ins recorded yet.", width=45).grid(
            row=0, column=0, columnspan=3
        )
        moving_avg_label.config(text="Moving Average: N/A")


def log_today(weight_entry, table_frame, moving_avg_label):
    try:
        weight = float(weight_entry.get())
        if weight <= 0:
            raise ValueError("Weight must be greater than zero.")
        insert_or_update_weigh_in(weight)
        messagebox.showinfo("Success", "Today's weight logged successfully!")
        weight_entry.delete(0, tk.END)
    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Error: {e}")
        weight_entry.delete(0, tk.END)
    update_display(table_frame, moving_avg_label)


def log_specific_date(date_entry, weight_entry, table_frame, moving_avg_label):
    try:
        date_str = date_entry.get()
        weight = float(weight_entry.get())
        if weight <= 0:
            raise ValueError("Weight must be greater than zero.")
        date = datetime.strptime(date_str.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")

        if datetime.strptime(date, "%Y-%m-%d") > datetime.now():
            raise ValueError("Date cannot be in the future.")

        insert_or_update_weigh_in_on_date(date, weight)
        messagebox.showinfo("Success", f"Weigh-in for {date} logged successfully!")
        weight_entry.delete(0, tk.END)

        today_date = datetime.now().strftime("%Y-%m-%d")
        date_entry.delete(0, tk.END)
        date_entry.insert(0, today_date)

    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Error: {e}")
        weight_entry.delete(0, tk.END)
    except IndexError:
        messagebox.showerror(
            "Invalid Input", "Please enter the date in YYYY-MM-DD format."
        )
    update_display(table_frame, moving_avg_label)


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


def insert_or_update_weigh_in(weight):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM weigh_ins WHERE date = ?", (today,))
    result = cursor.fetchone()

    if result:
        cursor.execute(
            "UPDATE weigh_ins SET weight = ? WHERE date = ?", (weight, today)
        )
    else:
        cursor.execute(
            "INSERT INTO weigh_ins (date, weight) VALUES (?, ?)", (today, weight)
        )

    conn.commit()
    conn.close()


def insert_or_update_weigh_in_on_date(date, weight):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weigh_ins WHERE date = ?", (date,))
    result = cursor.fetchone()

    if result:
        cursor.execute("UPDATE weigh_ins SET weight = ? WHERE date = ?", (weight, date))
    else:
        cursor.execute(
            "INSERT INTO weigh_ins (date, weight) VALUES (?, ?)", (date, weight)
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database()
    setup_gui()
