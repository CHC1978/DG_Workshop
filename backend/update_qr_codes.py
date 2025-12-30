"""Update all equipment QR code URLs with new domain"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import Equipment
from app.utils.asset_code import generate_qr_code_url

async def update_all_qr_codes():
    async with AsyncSessionLocal() as db:
        # Get all equipment
        result = await db.execute(select(Equipment))
        equipment_list = result.scalars().all()

        if len(equipment_list) == 0:
            print("No equipment found in database")
            return

        print(f"Found {len(equipment_list)} equipment")
        print("Updating QR code URLs...")
        print()

        updated_count = 0
        for eq in equipment_list:
            old_url = eq.qr_code
            new_url = generate_qr_code_url(eq.asset_code)

            if old_url != new_url:
                eq.qr_code = new_url
                print(f"  {eq.asset_code}:")
                print(f"    Old: {old_url}")
                print(f"    New: {new_url}")
                updated_count += 1
            else:
                print(f"  {eq.asset_code}: No change needed")

        if updated_count > 0:
            await db.commit()
            print()
            print(f"Updated {updated_count} QR code URLs")
        else:
            print()
            print("All QR codes are already up to date")

if __name__ == "__main__":
    print("QR Code URL Update Tool")
    print("=======================")
    print()

    from app.core.config import settings
    print(f"Current QR Code Domain: {settings.QR_CODE_DOMAIN}")
    print(f"Current Protocol: {settings.QR_CODE_PROTOCOL}")
    print()

    confirm = input("Update all QR codes with this domain? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        asyncio.run(update_all_qr_codes())
        print()
        print("Done! Remember to reprint QR code labels.")
    else:
        print("Cancelled")
