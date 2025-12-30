import sqlite3

conn = sqlite3.connect('data/marine_equipment.db')
cursor = conn.cursor()

# Check what columns exist
cursor.execute('PRAGMA table_info(equipment_logs)')
columns = cursor.fetchall()

print('equipment_logs columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

print()
print('Checking for edit tracking columns...')
col_names = [col[1] for col in columns]
edit_cols = ['edited_at', 'edited_by', 'edit_count', 'original_description', 'original_latitude', 'original_longitude']
for col in edit_cols:
    exists = col in col_names
    print(f'  {col}: {"EXISTS" if exists else "MISSING"}')

conn.close()
