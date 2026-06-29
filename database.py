import sqlite3

def init_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    

    # ================= USERS TABLE =================

    cursor.execute("""
 CREATE TABLE IF NOT EXISTS users (

    user_id INTEGER PRIMARY KEY AUTOINCREMENT,

    full_name TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    role TEXT NOT NULL DEFAULT 'Citizen',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
    """)

    # ================= COMPLAINTS TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (

    complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    tracking_id TEXT UNIQUE,

    title TEXT NOT NULL,

    description TEXT NOT NULL,

    category TEXT,

    priority TEXT DEFAULT 'Medium',

    status TEXT DEFAULT 'Pending',

    reply TEXT,

    ai_score INTEGER DEFAULT 0,

    location TEXT,

    evidence TEXT,

    latitude REAL,

    longitude REAL,

    ai_detected_ipc TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)

)
    """)

    # ================= COMPLAINT MEDIA TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_media (

        media_id INTEGER PRIMARY KEY AUTOINCREMENT,

        complaint_id INTEGER,

        file_path TEXT,

        file_type TEXT,

        deepfake_status TEXT DEFAULT 'Not Checked',

        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)

    )
    """)

    # ================= IPC SECTIONS TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ipc_sections (

        ipc_id INTEGER PRIMARY KEY AUTOINCREMENT,

        section_number TEXT NOT NULL,

        crime_keyword TEXT NOT NULL,

        description TEXT,

        punishment TEXT,

    )
    """)

    # ================= COMPLAINT IPC MAP =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_ipc_map (

        map_id INTEGER PRIMARY KEY AUTOINCREMENT,

        complaint_id INTEGER,

        ipc_id INTEGER,

        FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id),

        FOREIGN KEY (ipc_id)
        REFERENCES ipc_sections(ipc_id)

    )
    """)

    # ================= FIR TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fir (

        fir_id INTEGER PRIMARY KEY AUTOINCREMENT,

        complaint_id INTEGER,

        fir_number TEXT UNIQUE,

        crime_type TEXT,

        generated_text TEXT,

        status TEXT DEFAULT 'Draft',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)

    )
    """)

    # ================= AI LOGS TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_logs (

        log_id INTEGER PRIMARY KEY AUTOINCREMENT,

        complaint_id INTEGER,

        predicted_category TEXT,

        confidence_score REAL,

        detected_ipc TEXT,

        deepfake_result TEXT,

        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)

    )
    """)

    # ================= ACTIVITY LOGS TABLE =================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (

        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        action TEXT,

        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id)
        REFERENCES users(user_id)

    )
    """)

    # ================= INDEXES =================

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_id
    ON complaints(user_id)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_status
    ON complaints(status)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_priority
    ON complaints(priority)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_complaint_id
    ON complaint_media(complaint_id)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ipc_keyword
    ON ipc_sections(crime_keyword)
    """)

    conn.commit()
    conn.close()

    print("✅ All upgraded tables created successfully!")


if __name__ == "__main__":
    init_db()