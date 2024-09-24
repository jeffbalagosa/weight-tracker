import random
import sqlite3
from datetime import datetime, timedelta

MOCK_DATABASE_FILE = "weight_tracker_mock.db"


def create_mock_data():
    entries = []
    start_date = datetime.now() - timedelta(days=10)
    current_date = datetime.now()
    used_dates = set()
    for i in range(10):
        random_days = random.randint(1, 5)
        date = start_date + timedelta(days=random_days * i)
        if date > current_date:
            date = current_date
        date_str = date.strftime("%Y-%m-%d")
        if date_str in used_dates:
            continue
        used_dates.add(date_str)
        weight = round(190 + (i % 2) * 3 + (i * 0.5), 1)
        entries.append((date_str, weight))
    return entries


def setup_mock_database():
    conn = sqlite3.connect(MOCK_DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weigh_ins (
            date TEXT PRIMARY KEY,
            weight REAL
        )
        """
    )

    entries = create_mock_data()
    cursor.executemany("INSERT INTO weigh_ins (date, weight) VALUES (?, ?)", entries)

    conn.commit()
    conn.close()

    print(f"Mock data inserted into {MOCK_DATABASE_FILE}.")


if __name__ == "__main__":
    setup_mock_database()
