"""List all equipment in database"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import Equipment

async def list_all():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Equipment))
        equipment_list = result.scalars().all()

        print(f"Found {len(equipment_list)} equipment in database:")
        print()

        for eq in equipment_list:
            print(f"ID: {eq.id}")
            print(f"  Asset Code: {eq.asset_code}")
            print(f"  Manufacturer: {eq.manufacturer} {eq.model}")
            print(f"  Status: {eq.status}")
            print(f"  Active: {eq.is_active}")
            print()

if __name__ == "__main__":
    asyncio.run(list_all())
