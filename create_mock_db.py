import sqlite3
from datetime import datetime, timedelta

# Database file path for mock data
MOCK_DATABASE_FILE = "weight_tracker_mock.db"


# Mock data for 10 weigh-ins
def create_mock_data():
    # Generate mock entries for the past 10 days
    entries = []
    start_date = datetime.now() - timedelta(days=10)
    for i in range(10):
        # Increment the date for each entry
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        # Generate a mock weight, fluctuating between 190 and 200 lbs
        weight = round(190 + (i % 2) * 3 + (i * 0.5), 1)
        entries.append((date, weight))
    return entries


# Create the database and insert the mock data
def setup_mock_database():
    conn = sqlite3.connect(MOCK_DATABASE_FILE)
    cursor = conn.cursor()

    # Create the weigh_ins table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weigh_ins (
            date TEXT PRIMARY KEY,
            weight REAL
        )
        """
    )

    # Insert mock data
    entries = create_mock_data()
    cursor.executemany("INSERT INTO weigh_ins (date, weight) VALUES (?, ?)", entries)

    # Commit and close the connection
    conn.commit()
    conn.close()

    print(f"Mock data inserted into {MOCK_DATABASE_FILE}.")


# Run the mock database setup
if __name__ == "__main__":
    setup_mock_database()
