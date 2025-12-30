"""Clean all data and recreate test equipment"""
import asyncio
from sqlalchemy import delete
from app.core.database import AsyncSessionLocal
from app.models import Equipment, Location, LocationType, EquipmentLog
from app.utils.asset_code import generate_asset_code, generate_qr_code_url
from app.models.equipment import EquipmentCategory, EquipmentStatus

async def clean_and_recreate():
    async with AsyncSessionLocal() as db:
        print("Cleaning all equipment and locations...")

        # Delete all equipment logs
        await db.execute(delete(EquipmentLog))

        # Delete all equipment
        await db.execute(delete(Equipment))

        # Delete all locations
        await db.execute(delete(Location))

        await db.commit()
        print("All data cleaned!")

        # Create test location
        warehouse = Location(
            name="Main Warehouse",
            location_type=LocationType.WAREHOUSE,
            code="WH-001",
            is_active=True
        )
        db.add(warehouse)
        await db.flush()
        print(f"Created location: {warehouse.name} (ID: {warehouse.id})")

        # Create test equipment with ALL new fields
        asset_code = await generate_asset_code(EquipmentCategory.MBES, db)
        qr_code = generate_qr_code_url(asset_code)

        equipment = Equipment(
            asset_code=asset_code,
            qr_code=qr_code,
            category=EquipmentCategory.MBES,
            manufacturer="Kongsberg",
            model="EM2040C",
            serial_number="TEST-12345",
            status=EquipmentStatus.IN_STOCK,
            current_location_id=warehouse.id,
            deployed_to=None,
            deployed_by=None,
            purchase_date=None,
            photo_url=None,
            manual_url=None,
            calibration_report_url=None,
            last_maintenance_date=None,
            next_maintenance_date=None,
            maintenance_notes=None,
            specifications="Multibeam Echosounder - 200-400kHz",
            notes="Test equipment for system verification",
            is_active=True
        )

        db.add(equipment)
        await db.commit()
        await db.refresh(equipment)

        print(f"\nCreated equipment: {equipment.asset_code}")
        print(f"  Manufacturer: {equipment.manufacturer}")
        print(f"  Model: {equipment.model}")
        print(f"  Status: {equipment.status}")
        print(f"  Has deployed_to: {equipment.deployed_to is not None}")
        print(f"  Has deployed_by: {equipment.deployed_by is not None}")

        print("\nTest data recreated successfully!")
        print("You can now access equipment list and details")

if __name__ == "__main__":
    asyncio.run(clean_and_recreate())
