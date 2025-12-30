"""Delete specific equipment by asset code"""
import asyncio
import sys
from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models import Equipment, EquipmentLog

async def delete_equipment_by_asset_code(asset_code: str):
    async with AsyncSessionLocal() as db:
        # Find equipment
        result = await db.execute(
            select(Equipment).where(Equipment.asset_code == asset_code)
        )
        equipment = result.scalar_one_or_none()

        if not equipment:
            print(f"Equipment {asset_code} not found!")
            return False

        print(f"Found equipment:")
        print(f"  ID: {equipment.id}")
        print(f"  Asset Code: {equipment.asset_code}")
        print(f"  Manufacturer: {equipment.manufacturer} {equipment.model}")
        print(f"  Status: {equipment.status}")
        print()

        # Delete equipment logs first
        log_result = await db.execute(
            delete(EquipmentLog).where(EquipmentLog.equipment_id == equipment.id)
        )
        print(f"Deleted {log_result.rowcount} equipment logs")

        # Delete equipment
        await db.execute(
            delete(Equipment).where(Equipment.id == equipment.id)
        )

        await db.commit()
        print(f"Equipment {asset_code} deleted successfully!")
        return True

if __name__ == "__main__":
    asset_code = sys.argv[1] if len(sys.argv) > 1 else "MBES-2025-002"

    print(f"Deleting equipment: {asset_code}")
    print("=" * 50)
    print()

    asyncio.run(delete_equipment_by_asset_code(asset_code))
