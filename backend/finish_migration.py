import sqlite3

conn = sqlite3.connect('data/marine_equipment.db')
cursor = conn.cursor()

# Check if is_sub_equipment column exists
cursor.execute("PRAGMA table_info(equipment_logs)")
columns = cursor.fetchall()
has_is_sub_equipment = any(col[1] == 'is_sub_equipment' for col in columns)

print(f'is_sub_equipment column exists: {has_is_sub_equipment}')

# Check if sub_equipments table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sub_equipments'")
has_sub_equipments_table = cursor.fetchone() is not None

print(f'sub_equipments table exists: {has_sub_equipments_table}')

# If neither exists, we can try a clean migration
if not has_is_sub_equipment and not has_sub_equipments_table:
    print('Database is clean, ready for migration')
else:
    # Create sub_equipments table if it doesn't exist
    if not has_sub_equipments_table:
        print('Creating sub_equipments table...')
        cursor.execute('''
            CREATE TABLE sub_equipments (
                id INTEGER NOT NULL,
                parent_equipment_id INTEGER NOT NULL,
                asset_code VARCHAR(50) NOT NULL,
                qr_code VARCHAR(255) NOT NULL,
                component_name VARCHAR(100) NOT NULL,
                serial_number VARCHAR(100),
                status VARCHAR(11) NOT NULL,
                notes VARCHAR(500),
                is_active BOOLEAN NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                PRIMARY KEY (id),
                FOREIGN KEY(parent_equipment_id) REFERENCES equipments (id) ON DELETE CASCADE,
                UNIQUE (qr_code)
            )
        ''')

        cursor.execute('CREATE INDEX ix_sub_equipments_asset_code ON sub_equipments (asset_code)')
        cursor.execute('CREATE INDEX ix_sub_equipments_id ON sub_equipments (id)')
        cursor.execute('CREATE INDEX ix_sub_equipments_parent_equipment_id ON sub_equipments (parent_equipment_id)')
        cursor.execute('CREATE INDEX ix_sub_equipments_status ON sub_equipments (status)')

        conn.commit()
        print('sub_equipments table created successfully')

    print('Migration completed manually')

conn.close()
