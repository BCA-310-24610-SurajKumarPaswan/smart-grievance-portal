import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN tracking_id TEXT"
    )
    print("Tracking ID column added")
except:
    print("Tracking ID column already exists")

conn.commit()
conn.close()