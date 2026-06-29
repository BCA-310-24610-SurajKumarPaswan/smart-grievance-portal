import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN reply TEXT"
    )
    print("Reply column added")
except:
    print("Reply column already exists")

conn.commit()
conn.close()