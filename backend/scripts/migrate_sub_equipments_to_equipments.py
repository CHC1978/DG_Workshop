"""
將 sub_equipments 資料遷移到 equipments 表

執行方式:
cd backend
python scripts/migrate_sub_equipments_to_equipments.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.equipment import Equipment, EquipmentCategory
from app.models.sub_equipment import SubEquipment
from app.models.equipment_log import EquipmentLog, EquipmentLogType
from app.utils.asset_code import generate_qr_code_url


async def migrate_sub_equipments():
    """將所有 sub_equipments 遷移到 equipments"""

    # Create async engine
    # Convert sqlite:/// to sqlite+aiosqlite:/// for async operations
    db_url = str(settings.DATABASE_URL)
    if db_url.startswith('sqlite:///'):
        db_url = db_url.replace('sqlite:///', 'sqlite+aiosqlite:///', 1)

    engine = create_async_engine(
        db_url,
        echo=True
    )

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        try:
            # 1. 取得所有 sub_equipments
            result = await db.execute(
                select(SubEquipment).where(SubEquipment.is_active == True)
            )
            sub_equipments = result.scalars().all()

            print(f"Found {len(sub_equipments)} sub-equipments to migrate")

            migrated_count = 0

            for sub_eq in sub_equipments:
                # 2. 取得父設備資訊
                parent_result = await db.execute(
                    select(Equipment).where(Equipment.id == sub_eq.parent_equipment_id)
                )
                parent_equipment = parent_result.scalar_one_or_none()

                if not parent_equipment:
                    print(f"Warning: Parent equipment not found for sub-equipment {sub_eq.id}, skipping...")
                    continue

                # 3. 生成 Asset Code (格式: {Parent_Code}-{Component_Name}-{Seq})
                # 例如: MBES-EM2040-0001-TDC-001
                # 簡化版：使用 component_name 的前3個字母作為代碼
                component_code = sub_eq.component_name[:3].upper()

                # 取得同一父設備下的子設備數量來生成序號
                existing_children_result = await db.execute(
                    select(Equipment).where(
                        Equipment.parent_equipment_id == parent_equipment.id,
                        Equipment.is_active == True
                    )
                )
                existing_children_count = len(existing_children_result.scalars().all())
                seq_num = existing_children_count + 1

                asset_code = f"{parent_equipment.asset_code}-{component_code}-{seq_num:03d}"
                qr_code = generate_qr_code_url(asset_code)

                # 4. 創建新的 Equipment (作為子設備)
                new_equipment = Equipment(
                    asset_code=asset_code,
                    qr_code=qr_code,
                    category=parent_equipment.category,  # 繼承父設備的 category
                    manufacturer=parent_equipment.manufacturer,  # 使用父設備的 manufacturer
                    model=sub_eq.component_name,  # component_name 作為 model
                    serial_number=sub_eq.serial_number,
                    status=parent_equipment.status,  # 繼承父設備的狀態
                    current_location_id=parent_equipment.current_location_id,  # 繼承父設備的位置
                    project_id=parent_equipment.project_id,  # 繼承父設備的專案
                    parent_equipment_id=parent_equipment.id,  # 設定父設備
                    notes=sub_eq.notes,
                    is_active=True
                )

                db.add(new_equipment)
                await db.flush()  # 取得新設備的 ID

                # 5. 創建遷移日誌
                log = EquipmentLog(
                    equipment_id=new_equipment.id,
                    log_type=EquipmentLogType.CREATED,
                    description=f"Migrated from sub-equipment (original ID: {sub_eq.id})",
                    new_value=f"Parent: {parent_equipment.asset_code}, Component: {sub_eq.component_name}",
                )
                db.add(log)

                # 6. 停用原本的 sub_equipment（不刪除，保留備份）
                sub_eq.is_active = False

                migrated_count += 1
                print(f"Migrated: {sub_eq.component_name} -> {asset_code}")

            # 7. 提交所有變更
            await db.commit()

            print(f"\n[SUCCESS] Migration completed successfully!")
            print(f"Total migrated: {migrated_count} sub-equipments")
            print(f"Note: Original sub_equipments are marked as inactive (is_active=False)")

        except Exception as e:
            await db.rollback()
            print(f"\n[ERROR] Migration failed: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("=== Sub-Equipment to Equipment Migration ===")
    print("This script will migrate all sub_equipments to equipments table")
    print("Original sub_equipments will be marked as inactive\n")

    confirm = input("Continue? (yes/no): ")
    if confirm.lower() == "yes":
        asyncio.run(migrate_sub_equipments())
    else:
        print("Migration cancelled")
