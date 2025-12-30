"""Manually add report_url column to calibrations table"""
import sqlite3

db_path = 'data/marine_equipment.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute("PRAGMA table_info(calibrations)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'report_url' in columns:
        print("Column 'report_url' already exists")
    else:
        cursor.execute("ALTER TABLE calibrations ADD COLUMN report_url VARCHAR(500)")
        conn.commit()
        print("Column 'report_url' added successfully")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
