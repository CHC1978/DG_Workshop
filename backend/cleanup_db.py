import sqlite3

conn = sqlite3.connect('data/marine_equipment.db')
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sub_equipments'")
result = cursor.fetchone()

print(f'sub_equipments table exists: {result is not None}')

if result:
    cursor.execute('DROP TABLE sub_equipments')
    conn.commit()
    print('sub_equipments table dropped successfully')
else:
    print('sub_equipments table does not exist')

conn.close()
