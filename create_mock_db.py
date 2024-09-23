import sqlite3
from datetime import datetime, timedelta

MOCK_DATABASE_FILE = "weight_tracker_mock.db"


def create_mock_data():

    entries = []
    start_date = datetime.now() - timedelta(days=10)
    for i in range(10):

        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

        weight = round(190 + (i % 2) * 3 + (i * 0.5), 1)
        entries.append((date, weight))
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
