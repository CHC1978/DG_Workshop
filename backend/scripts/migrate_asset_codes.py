"""
Asset Code Migration Script

將設備從舊格式 (MBES-2024-001) 遷移至新格式 (MBES-EM2040C-SN12345 或 MBES-EM2040C-0001)

執行前請務必備份資料庫！

使用方法:
    cd backend
    python scripts/migrate_asset_codes.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.equipment import Equipment, EquipmentCategory
from app.models.equipment_log import EquipmentLog, EquipmentLogType
from app.utils.asset_code import clean_model_code, generate_qr_code_url


async def migrate_equipment_asset_codes(dry_run: bool = True) -> None:
    """
    遷移所有設備的 Asset Code 至新格式

    Args:
        dry_run: True = 僅預覽變更，False = 實際執行變更
    """
    async with AsyncSessionLocal() as db:
        # 查詢所有啟用的設備
        result = await db.execute(
            select(Equipment)
            .where(Equipment.is_active == True)
            .order_by(Equipment.id)
        )
        equipments = result.scalars().all()

        if not equipments:
            print("⚠️  No equipment found in database")
            return

        print(f"\n{'=' * 80}")
        print(f"Asset Code Migration - {'DRY RUN' if dry_run else 'LIVE MODE'}")
        print(f"{'=' * 80}\n")
        print(f"Found {len(equipments)} equipment to process\n")

        success_count = 0
        skip_count = 0
        error_count = 0

        for eq in equipments:
            try:
                # 解析舊格式 Asset Code
                old_asset_code = eq.asset_code
                parts = old_asset_code.split('-')

                # 檢查是否已經是新格式 (至少3個部分，且第二部分不是年份)
                if len(parts) >= 3:
                    second_part = parts[1]
                    # 如果第二部分不是4位數字（年份），則可能已是新格式
                    if not (second_part.isdigit() and len(second_part) == 4):
                        print(f"⏭️  SKIP: {old_asset_code} - Already in new format")
                        skip_count += 1
                        continue

                # 舊格式: CATEGORY-YEAR-SEQUENCE
                if len(parts) != 3:
                    print(f"❌ ERROR: {old_asset_code} - Invalid format (expected 3 parts)")
                    error_count += 1
                    continue

                category_str, year, seq = parts

                # 生成新的 model_code
                model_code = clean_model_code(eq.model)

                # 生成新的 Asset Code
                if eq.serial_number:
                    # 有序號：使用 SN 格式
                    new_asset_code = f"{category_str}-{model_code}-SN{eq.serial_number}"
                else:
                    # 無序號：使用序號格式（保留舊序號）
                    new_asset_code = f"{category_str}-{model_code}-{seq.zfill(4)}"

                # 生成新的 QR Code
                new_qr_code = generate_qr_code_url(new_asset_code)

                # 顯示變更
                print(f"📦 Equipment ID: {eq.id}")
                print(f"   Model: {eq.model}")
                print(f"   Serial: {eq.serial_number or 'N/A'}")
                print(f"   Old: {old_asset_code}")
                print(f"   New: {new_asset_code}")
                print(f"   Model Code: {model_code}")

                if not dry_run:
                    # 更新設備
                    eq.asset_code = new_asset_code
                    eq.qr_code = new_qr_code
                    eq.model_code = model_code

                    # 建立 Log 記錄
                    log = EquipmentLog(
                        equipment_id=eq.id,
                        log_type=EquipmentLogType.UPDATED,
                        description=f"Asset Code migrated from {old_asset_code} to {new_asset_code}"
                    )
                    db.add(log)

                    print("   ✅ Updated")
                else:
                    print("   🔍 Preview (not saved)")

                print()
                success_count += 1

            except Exception as e:
                print(f"❌ ERROR processing equipment {eq.id}: {str(e)}\n")
                error_count += 1
                continue

        # 提交變更（僅在非 dry_run 模式）
        if not dry_run:
            await db.commit()
            print(f"\n{'=' * 80}")
            print("✅ Migration completed and changes committed to database")
        else:
            print(f"\n{'=' * 80}")
            print("🔍 Dry run completed - no changes were made to database")

        print(f"{'=' * 80}\n")
        print(f"📊 Summary:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ⏭️  Skipped: {skip_count}")
        print(f"   ❌ Errors:  {error_count}")
        print(f"   📝 Total:   {len(equipments)}\n")


async def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate equipment asset codes from old format to new format"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute migration (default is dry-run mode)"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm execution (required with --live)"
    )

    args = parser.parse_args()

    # 安全檢查
    if args.live:
        if not args.confirm:
            print("❌ Error: --live mode requires --confirm flag")
            print("   Example: python scripts/migrate_asset_codes.py --live --confirm")
            return

        print("\n⚠️  WARNING: You are about to modify the database in LIVE mode!")
        print("⚠️  Please ensure you have backed up the database before proceeding.\n")

        response = input("Type 'YES' to continue, or anything else to cancel: ")
        if response != "YES":
            print("❌ Migration cancelled")
            return

    # 執行遷移
    await migrate_equipment_asset_codes(dry_run=not args.live)


if __name__ == "__main__":
    asyncio.run(main())
