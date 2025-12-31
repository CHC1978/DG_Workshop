"""Verify sub-equipment migration results"""
import sqlite3

# Connect to database
conn = sqlite3.connect('data/marine_equipment.db')
cursor = conn.cursor()

print("=" * 80)
print("Sub-Equipment Migration Verification")
print("=" * 80)

# Check child equipment
print("\n1. Child Equipment (with parent_equipment_id):")
print("-" * 80)
result = cursor.execute("""
    SELECT e.id, e.asset_code, e.model, e.parent_equipment_id, p.asset_code as parent_code
    FROM equipments e
    LEFT JOIN equipments p ON e.parent_equipment_id = p.id
    WHERE e.parent_equipment_id IS NOT NULL
""").fetchall()

print(f"{'ID':<5} {'Asset Code':<35} {'Model':<25} {'Parent':<10} {'Parent Code':<25}")
print("-" * 80)
for r in result:
    print(f"{r[0]:<5} {r[1]:<35} {r[2]:<25} {r[3]:<10} {r[4] or 'N/A':<25}")

# Check migration logs
print("\n2. Migration Activity Logs:")
print("-" * 80)
result = cursor.execute("""
    SELECT equipment_id, log_type, description, created_at
    FROM equipment_logs
    WHERE equipment_id IN (6, 7, 8) AND log_type = 'CREATED'
    ORDER BY id DESC
""").fetchall()

print(f"{'Eq ID':<8} {'Type':<10} {'Description':<50} {'Created At':<20}")
print("-" * 80)
for r in result:
    desc = r[2][:47] + "..." if len(r[2]) > 50 else r[2]
    print(f"{r[0]:<8} {r[1]:<10} {desc:<50} {r[3]:<20}")

# Check inactive sub_equipments
print("\n3. Inactive Sub-Equipments (original records):")
print("-" * 80)
result = cursor.execute("""
    SELECT id, asset_code, component_name, is_active
    FROM sub_equipments
    WHERE is_active = 0
    ORDER BY id DESC
    LIMIT 5
""").fetchall()

print(f"{'ID':<5} {'Asset Code':<35} {'Component Name':<30} {'Active':<10}")
print("-" * 80)
for r in result:
    print(f"{r[0]:<5} {r[1]:<35} {r[2]:<30} {r[3]:<10}")

conn.close()

print("\n" + "=" * 80)
print("Verification Complete!")
print("=" * 80)
