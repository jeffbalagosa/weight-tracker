import os
import sqlite3
from datetime import datetime

# Database file path
DATABASE_FILE = "weight_tracker.db"


# Check if the database exists and create it if not
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


# Fetch the last 10 weigh-ins and calculate the differences and the average
def get_last_10_entries():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT date, weight FROM weigh_ins ORDER BY date DESC LIMIT 10")
    entries = cursor.fetchall()

    conn.close()

    if not entries:
        print("No weigh-ins have been recorded yet. Please add your first entry!")
        return []

    # Reverse order to get earliest first
    entries = entries[::-1]

    print("\nLast 10 Weigh-ins:")
    print("|    Date    |  Weight  | Difference |")
    print("|------------|----------|------------|")

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

        print(f"| {date} | {weight:.1f} lbs | {difference:>10} |")
        previous_weight = weight
        differences.append(difference)

    average_weight = sum([entry[1] for entry in entries]) / len(entries)
    print(f"\nAverage: {average_weight:.2f} lbs")

    return entries


# Insert or update today's weigh-in
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
    print(f"Weigh-in for {today} recorded/updated successfully.")


# Insert or update weigh-in for a specific date
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
    print(f"Weigh-in for {date} recorded/updated successfully.")


# Main function that handles user input and interaction
def main():
    setup_database()

    while True:
        print("\nMain Screen")
        entries = get_last_10_entries()

        print("\nCommands:")
        print(" - /w to enter or adjust today's weigh-in.")
        print(" - /a to enter or adjust a weigh-in for a different day.")
        print(" - Ctrl + c to quit the application.")
        print("")

        command = input("Enter command: ").strip()

        if command == "/w":
            print("\nPlease enter today's weight: ")
            try:
                weight = float(input("Weight: ").strip())
                insert_or_update_weigh_in(weight)
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
                insert_or_update_weigh_in_on_date(date, weight)
            except (ValueError, IndexError):
                print(
                    "Invalid format. Please enter the date in YYYY-MM-DD format and a numeric weight."
                )
            continue


if __name__ == "__main__":
    main()
