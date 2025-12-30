"""Test equipment list API"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import Equipment

async def test():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Equipment))
        equipment_list = result.scalars().all()

        print(f"Found {len(equipment_list)} equipment in database")

        for eq in equipment_list:
            print(f"  {eq.asset_code}: {eq.manufacturer} {eq.model} - Status: {eq.status}")
            print(f"    Has photo_url: {eq.photo_url is not None}")
            print(f"    Has manual_url: {eq.manual_url is not None}")
            print(f"    Has calibration_report_url: {eq.calibration_report_url is not None}")

if __name__ == "__main__":
    asyncio.run(test())
