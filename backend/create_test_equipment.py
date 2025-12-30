"""Create test equipment"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models import Equipment, Location, LocationType
from app.utils.asset_code import generate_asset_code, generate_qr_code_url
from app.models.equipment import EquipmentCategory, EquipmentStatus

async def create_test_data():
    async with AsyncSessionLocal() as db:
        # Create a test location first
        warehouse = Location(
            name="Main Warehouse",
            location_type=LocationType.WAREHOUSE,
            code="WH-001",
            is_active=True
        )
        db.add(warehouse)
        await db.flush()

        print(f"Created location: {warehouse.name} (ID: {warehouse.id})")

        # Create test equipment
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
            purchase_date=None,
            photo_url=None,
            manual_url=None,
            calibration_report_url=None,
            specifications="Test equipment for system verification",
            notes="Created by test script",
            is_active=True
        )

        db.add(equipment)
        await db.commit()
        await db.refresh(equipment)

        print(f"Created equipment: {equipment.asset_code}")
        print(f"  Manufacturer: {equipment.manufacturer}")
        print(f"  Model: {equipment.model}")
        print(f"  Status: {equipment.status}")
        print(f"  QR Code: {equipment.qr_code}")

        print("\nTest data created successfully!")

if __name__ == "__main__":
    asyncio.run(create_test_data())
