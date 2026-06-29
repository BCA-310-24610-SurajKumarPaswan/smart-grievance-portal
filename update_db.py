import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ai_score column
try:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN ai_score INTEGER DEFAULT 0"
    )
    print("✅ ai_score column added successfully!")
except:
    print("⚠ ai_score already exists")

# location column
try:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN location TEXT"
    )
    print("✅ location column added successfully!")
except:
    print("⚠ location already exists")

# reply column
try:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN reply TEXT"
    )
    print("✅ reply column added successfully!")
except:
    print("⚠ reply already exists")

# evidence column
try:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN evidence TEXT"
    )
    print("✅ evidence column added successfully!")
except:
    print("⚠ evidence already exists")

conn.commit()
conn.close()

print("🎉 Database updated successfully!")