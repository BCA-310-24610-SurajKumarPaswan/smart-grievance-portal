import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN evidence TEXT"
    )
    print("Evidence column added")
except:
    print("Evidence already exists")

conn.commit()
conn.close()