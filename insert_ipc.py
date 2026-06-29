import sqlite3

def insert_ipc_sections():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    ipc_data = [
        ("379", "theft steal", "Theft of property", "Imprisonment up to 3 years or fine or both"),
        ("420", "fraud cheating scam", "Cheating and dishonestly inducing delivery of property", "Imprisonment up to 7 years and fine"),
        ("354", "harassment molest", "Assault or criminal force against woman", "Imprisonment up to 5 years and fine"),
        ("506", "threat intimidation", "Criminal intimidation", "Imprisonment up to 2 years or fine or both"),
        ("509", "insult woman", "Word or gesture intended to insult modesty of a woman", "Imprisonment up to 3 years and fine"),
        ("323", "assault hurt", "Voluntarily causing hurt", "Imprisonment up to 1 year or fine or both"),
        ("406", "breach trust", "Criminal breach of trust", "Imprisonment up to 3 years or fine or both"),
        ("468", "forgery fake", "Forgery for purpose of cheating", "Imprisonment up to 7 years and fine"),
        ("471", "fake document", "Using forged document as genuine", "Imprisonment up to 7 years and fine"),
        ("354D", "stalking follow", "Following or contacting a woman repeatedly", "Imprisonment up to 3 years and fine"),
        ("499", "defamation", "Defamation", "Imprisonment up to 2 years or fine or both"),
        ("384", "extortion blackmail", "Extortion", "Imprisonment up to 3 years or fine or both"),
        ("302", "murder kill death", "Punishment for murder", "Life imprisonment / death penalty"),
    ]

    for section_number, keywords, description, punishment in ipc_data:
        cursor.execute("""
            INSERT OR IGNORE INTO ipc_sections
            (section_number, keywords, description, punishment)
            VALUES (?, ?, ?, ?)
        """, (section_number, keywords, description, punishment))

    conn.commit()
    conn.close()
    print("✅ IPC sections inserted successfully!")

if __name__ == "__main__":
    insert_ipc_sections()  