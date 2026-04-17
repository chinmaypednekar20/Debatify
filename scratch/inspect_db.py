import sqlite3
import os

db_path = 'debatify.db'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Debates ---")
    cursor.execute("SELECT id, title, date, source_file, created_at FROM debates ORDER BY date ASC, created_at DESC")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    
    conn.close()
