import os
import sqlite3
from datetime import datetime

# Database file path
DATABASE_FILE = "weight_tracker.db"


def setup_database():
    """
    Sets up the database for storing weight entries.

    This function checks if the database file specified by DATABASE_FILE exists.
    If it does not exist, it creates a new SQLite database file and a table named
    'weigh_ins' with columns 'date' (TEXT, primary key) and 'weight' (REAL).

    Returns:
        None
    """
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


def get_last_10_entries():
    """
    Retrieves and displays the last 10 weight entries from the database.
    Connects to the SQLite database specified by DATABASE_FILE, fetches the last
    10 weigh-in entries ordered by date in descending order, and then displays
    them in ascending order. Each entry includes the date, weight, and the
    difference in weight from the previous entry. If no entries are found, a
    message is printed indicating that no weigh-ins have been recorded yet.
    Returns:
        list: A list of tuples, each containing the date and weight of the last
              10 weigh-ins in ascending order. If no entries are found, an empty
              list is returned.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT date, weight FROM weigh_ins ORDER BY date DESC LIMIT 10")
    entries = cursor.fetchall()

    conn.close()

    if not entries:
        print("No weigh-ins have been recorded yet. Please add your first entry!")
        return []

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
    print(f"\nMoving Average: {average_weight:.2f} lbs")

    return entries


def insert_or_update_weigh_in(weight):
    """
    Inserts or updates the weigh-in record for the current date in the database.
    If a weigh-in record already exists for today, it updates the weight.
    Otherwise, it inserts a new record with today's date and the provided weight.
    Args:
        weight (float): The weight to be recorded or updated for today.
    Raises:
        sqlite3.DatabaseError: If there is an issue with the database connection or execution.
    """
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


def insert_or_update_weigh_in_on_date(date, weight):
    """
    Inserts a new weigh-in record or updates an existing one for a given date.
    This function connects to the SQLite database specified by DATABASE_FILE,
    checks if a weigh-in record exists for the provided date, and either updates
    the existing record with the new weight or inserts a new record if none exists.
    Args:
        date (str): The date of the weigh-in in the format 'YYYY-MM-DD'.
        weight (float): The weight to be recorded or updated.
    Returns:
        None
    """
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


def main():
    """
    Main function to run the weight tracker application.
    This function sets up the database and enters an infinite loop to display the main screen,
    fetch the last 10 entries, and handle user commands. The available commands are:
     - /w: Enter or adjust today's weigh-in.
     - /a: Enter or adjust a weigh-in for a different day.
     - Ctrl + c: Quit the application.
    Commands are processed in a loop, and appropriate functions are called to handle the
    weigh-in entries. Input validation is performed to ensure correct data formats.
    Raises:
        ValueError: If the input weight is not a valid float.
        IndexError: If the input date and weight are not in the correct format.
    """
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
