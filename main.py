import os
import sqlite3
from datetime import datetime

DATABASE_FILE = "weight_tracker.db"


def setup_database(db_file):
    if not os.path.exists(db_file):
        with sqlite3.connect(db_file) as conn:
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


def fetch_last_entries(db_file, limit=10):
    try:
        with sqlite3.connect(db_file) as conn:
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


def display_entries(entries):
    if not entries:
        print("No weigh-ins have been recorded yet. Please add your first entry!")
        return

    print("\nLast 10 Weigh-ins:")
    print("|------------|-----------|-------------|")
    print("|    Date    |  Weight   | Difference  |")
    print("|------------|-----------|-------------|")

    for date, weight, difference in entries:
        print(f"| {date} | {weight:.1f} lbs |  {difference:>10} |")

    average_weight = sum([entry[1] for entry in entries]) / len(entries)
    print("\n" + "*" * 30)
    print(f"Moving Average: {average_weight:.1f} lbs")
    print("*" * 30)


def get_last_10_entries(db_file):
    entries = fetch_last_entries(db_file)
    if not entries:
        return []

    entries_with_differences = calculate_differences(entries)
    display_entries(entries_with_differences)
    return entries


def insert_or_update_weigh_in(db_file, date, weight):
    try:
        with sqlite3.connect(db_file) as conn:
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
            print(f"\nWeigh-in for {date} recorded/updated successfully.")
    except sqlite3.Error as e:
        print(f"\nDatabase error: {e}")


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


def main():
    setup_database(DATABASE_FILE)

    while True:
        purge_records(DATABASE_FILE, years=10)
        print("\n# Main Screen")

        entries_arr_length = len(fetch_last_entries(DATABASE_FILE))
        if not entries_arr_length:
            print("\nNo weigh-ins have been recorded yet. Please add your first entry!")

        else:
            get_last_10_entries(DATABASE_FILE)

        print("\n## Commands:")
        print(" - /w to enter or adjust today's weigh-in.")
        print(" - /a to enter or adjust a weigh-in for a different day.")
        print(" - /s to start over (purge all records).")
        print(" - Ctrl + c to quit the application.")
        print("")

        command = input("Enter command: ").strip()

        if command == "/w":
            print("\nPlease enter today's weight: ")
            try:
                weight = float(input("Weight: ").strip())
                today = datetime.now().strftime("%Y-%m-%d")
                insert_or_update_weigh_in(DATABASE_FILE, today, weight)
            except ValueError:
                print("Invalid input. Please enter a numeric weight.")
            continue

        elif command == "/a":
            print("\nPlease enter the date and weight [example: 2024-09-01, 180.5]: ")
            entry = input().strip()
            try:
                date_str, weight_str = entry.split(",")
                date = datetime.strptime(date_str.strip(), "%Y-%m-%d").strftime(
                    "%Y-%m-%d"
                )
                weight = float(weight_str.strip())
                insert_or_update_weigh_in(DATABASE_FILE, date, weight)
            except (ValueError, IndexError):
                print(
                    "\nInvalid format. Please enter the date in YYYY-MM-DD format and a numeric weight."
                )
            continue

        elif command == "/s":
            print("\nAre you sure you want to delete all records? (y/n)")
            confirm = input().strip().lower()
            if confirm == "y":
                purge_records(DATABASE_FILE)
                print("\nAll records have been deleted.")
            continue


if __name__ == "__main__":
    main()
