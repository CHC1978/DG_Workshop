#!/usr/bin/env python
"""
Update QR Code URLs for NAS deployment
Target: neptus-station.boga-ulmer.ts.net:8443

Usage on NAS:
1. Copy this file to /volume1/docker/marine-equipment/
2. Run via Task Scheduler:
   docker cp /volume1/docker/marine-equipment/update_qr_codes_nas.py marine-equipment-backend:/app/
   docker exec marine-equipment-backend python update_qr_codes_nas.py
"""
import asyncio
from datetime import datetime

# Target domain configuration
DOMAIN = 'neptus-station.boga-ulmer.ts.net:8443'
PROTOCOL = 'https'


async def update_qr_codes():
    """Update all equipment QR codes to new domain"""
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models import Equipment

    print("=" * 50)
    print("QR Code Update Script")
    print("=" * 50)
    print(f"Start time: {datetime.now()}")
    print(f"Target domain: {DOMAIN}")
    print(f"Protocol: {PROTOCOL}")
    print("")

    print("Connecting to database...")
    async with AsyncSessionLocal() as db:
        print("Fetching all equipment...")
        result = await db.execute(select(Equipment))
        equipment_list = result.scalars().all()

        total = len(equipment_list)
        print(f"Found {total} equipment records")
        print("")
        print("-" * 50)

        updated_count = 0
        for eq in equipment_list:
            old_url = eq.qr_code or "None"
            new_url = f"{PROTOCOL}://{DOMAIN}/e/{eq.asset_code}"

            print(f"Equipment: {eq.asset_code}")
            print(f"  Old URL: {old_url}")
            print(f"  New URL: {new_url}")

            if old_url != new_url:
                eq.qr_code = new_url
                print("  Status: UPDATED")
                updated_count += 1
            else:
                print("  Status: No change")
            print("")

        print("-" * 50)
        print("Committing changes to database...")
        await db.commit()
        print("")
        print("=" * 50)
        print(f"SUMMARY")
        print(f"  Total equipment: {total}")
        print(f"  Updated: {updated_count}")
        print(f"  Unchanged: {total - updated_count}")
        print("=" * 50)
        print(f"End time: {datetime.now()}")
        print("")

        if updated_count > 0:
            print("QR codes updated successfully!")
            print("Please reprint QR code labels if needed.")
        else:
            print("All QR codes are already up to date.")


if __name__ == "__main__":
    asyncio.run(update_qr_codes())
