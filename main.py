import os
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Database file path
DATABASE_FILE = "weight_tracker.db"


# GUI setup
def setup_gui():
    root = tk.Tk()
    root.title("Weight Tracker")
    root.geometry("500x400")  # Adjusted window size if needed

    # Frame for input fields
    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    # Weight Entry Field
    weight_label = tk.Label(input_frame, text="Enter Weight (lbs):")
    weight_label.grid(row=0, column=0, padx=10, pady=10)
    weight_entry = tk.Entry(input_frame)
    weight_entry.grid(row=0, column=1, padx=10, pady=10)

    # Button to log today's weight
    log_button = tk.Button(
        input_frame,
        text="Log Today's Weight",
        command=lambda: log_today(weight_entry, table_frame, moving_avg_label),
    )
    log_button.grid(row=1, column=0, columnspan=2, pady=5)  # Reduced bottom padding

    # Button to log weight for a specific date
    specific_date_label = tk.Label(input_frame, text="Enter Date (YYYY-MM-DD):")
    specific_date_label.grid(row=2, column=0, padx=10, pady=5)
    date_entry = tk.Entry(input_frame)
    date_entry.grid(row=2, column=1, padx=10, pady=5)

    # Button to log weight for the specific date
    specific_log_button = tk.Button(
        input_frame,
        text="Log Weight for Date",
        command=lambda: log_specific_date(
            date_entry, weight_entry, table_frame, moving_avg_label
        ),
    )
    specific_log_button.grid(row=3, column=0, columnspan=2, pady=5)

    # Display Area for the last 10 weigh-ins and moving average
    display_frame = tk.Frame(root)
    display_frame.pack(pady=5)  # Reduced bottom padding to avoid excess space

    display_label = tk.Label(display_frame, text="Last 10 Weigh-Ins:")
    display_label.pack()

    # Frame to hold the table
    table_frame = tk.Frame(display_frame)
    table_frame.pack(pady=(5, 0))  # Reduced bottom padding, top is fine for separation

    # Label for moving average
    moving_avg_label = tk.Label(display_frame, text="Moving Average: ")
    moving_avg_label.pack(pady=(5, 0))  # Removed excessive padding at the bottom

    # Initial call to display the last 10 entries and moving average
    update_display(table_frame, moving_avg_label)

    root.mainloop()


# Update display with the last 10 entries and moving average
def update_display(table_frame, moving_avg_label):
    # Clear the table before displaying new data
    for widget in table_frame.winfo_children():
        widget.destroy()

    entries = get_last_10_entries()

    if entries:
        total_weight = 0

        # Create table headers
        tk.Label(
            table_frame, text="Date", borderwidth=1, relief="solid", width=15
        ).grid(row=0, column=0)
        tk.Label(
            table_frame, text="Weight (lbs)", borderwidth=1, relief="solid", width=15
        ).grid(row=0, column=1)
        tk.Label(
            table_frame, text="Difference", borderwidth=1, relief="solid", width=15
        ).grid(row=0, column=2)

        # Populate table with the last 10 entries
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

        # Calculate and display the moving average
        moving_avg = total_weight / len(entries)
        moving_avg_label.config(text=f"Moving Average: {moving_avg:.2f} lbs")
    else:
        # If no entries are available, display a message
        tk.Label(table_frame, text="No weigh-ins recorded yet.", width=45).grid(
            row=0, column=0, columnspan=3
        )
        moving_avg_label.config(text="Moving Average: N/A")


# Log today's weight from input
def log_today(weight_entry, table_frame, moving_avg_label):
    try:
        weight = float(weight_entry.get())
        insert_or_update_weigh_in(weight)
        messagebox.showinfo("Success", "Today's weight logged successfully!")
        weight_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid numeric weight.")
    update_display(table_frame, moving_avg_label)


# Log weight for a specific date
def log_specific_date(date_entry, weight_entry, table_frame, moving_avg_label):
    try:
        date_str = date_entry.get()
        weight = float(weight_entry.get())
        date = datetime.strptime(date_str.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
        insert_or_update_weigh_in_on_date(date, weight)
        messagebox.showinfo("Success", f"Weigh-in for {date} logged successfully!")
        date_entry.delete(0, tk.END)
        weight_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a valid date in YYYY-MM-DD format and a numeric weight.",
        )
    update_display(table_frame, moving_avg_label)


# Database setup function remains unchanged
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


# Remaining backend functions (unchanged)
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
