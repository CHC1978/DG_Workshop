"""
Manual Migration Fix

Execute remaining migration steps manually since projects table already exists
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def check_and_fix_migration():
    """Check and fix migration"""
    async with AsyncSessionLocal() as db:
        print("Checking database structure...\n")

        # Check if projects table exists
        result = await db.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='projects'"
        ))
        projects_exists = result.scalar_one_or_none()
        print(f"[OK] projects table exists: {projects_exists is not None}")

        # Check locations table new columns
        result = await db.execute(text("PRAGMA table_info(locations)"))
        location_columns = {row[1] for row in result.fetchall()}

        new_location_columns = [
            'vessel_mmsi', 'vessel_national_id', 'vessel_internal_code',
            'vessel_name', 'vessel_flag', 'vessel_type', 'vessel_owner',
            'person_name', 'person_contact', 'employee_id', 'department',
            'current_project_id'
        ]

        missing_location_columns = [col for col in new_location_columns if col not in location_columns]

        if missing_location_columns:
            print(f"\n[WARN] locations table missing columns: {missing_location_columns}")
            print("Adding columns...")

            for col in missing_location_columns:
                if col == 'current_project_id':
                    await db.execute(text("ALTER TABLE locations ADD COLUMN current_project_id INTEGER"))
                elif col.startswith('vessel_'):
                    length = {
                        'vessel_mmsi': 9,
                        'vessel_national_id': 30,
                        'vessel_internal_code': 20,
                        'vessel_name': 100,
                        'vessel_flag': 50,
                        'vessel_type': 50,
                        'vessel_owner': 100
                    }[col]
                    await db.execute(text(f"ALTER TABLE locations ADD COLUMN {col} VARCHAR({length})"))
                else:  # person columns
                    length = {
                        'person_name': 100,
                        'person_contact': 100,
                        'employee_id': 30,
                        'department': 100
                    }[col]
                    await db.execute(text(f"ALTER TABLE locations ADD COLUMN {col} VARCHAR({length})"))
                print(f"  [OK] Added {col}")

            await db.commit()
            print("[OK] locations table updated")
        else:
            print("[OK] locations table already has all new columns")

        # Check equipments table new columns
        result = await db.execute(text("PRAGMA table_info(equipments)"))
        equipment_columns = {row[1] for row in result.fetchall()}

        new_equipment_columns = [
            'model_code', 'project_id', 'installation_type',
            'installation_date', 'installation_notes'
        ]

        missing_equipment_columns = [col for col in new_equipment_columns if col not in equipment_columns]

        if missing_equipment_columns:
            print(f"\n[WARN] equipments table missing columns: {missing_equipment_columns}")
            print("Adding columns...")

            for col in missing_equipment_columns:
                if col == 'model_code':
                    await db.execute(text("ALTER TABLE equipments ADD COLUMN model_code VARCHAR(50)"))
                elif col == 'project_id':
                    await db.execute(text("ALTER TABLE equipments ADD COLUMN project_id INTEGER"))
                elif col == 'installation_type':
                    await db.execute(text("ALTER TABLE equipments ADD COLUMN installation_type VARCHAR(20)"))
                elif col == 'installation_date':
                    await db.execute(text("ALTER TABLE equipments ADD COLUMN installation_date DATE"))
                elif col == 'installation_notes':
                    await db.execute(text("ALTER TABLE equipments ADD COLUMN installation_notes TEXT"))
                print(f"  [OK] Added {col}")

            await db.commit()
            print("[OK] equipments table updated")
        else:
            print("[OK] equipments table already has all new columns")

        print("\n" + "=" * 60)
        print("[SUCCESS] Migration fix completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(check_and_fix_migration())
