"""
Equipment Service - Business logic for equipment management
"""
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models.equipment import Equipment, EquipmentStatus, EquipmentCategory
from app.models.equipment_log import EquipmentLog, EquipmentLogType
from app.models.location import Location
from app.models.project import Project

logger = logging.getLogger(__name__)


class EquipmentService:
    """Service class for equipment business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Logging ====================

    async def log_equipment_change(
        self,
        equipment_id: int,
        log_type: EquipmentLogType,
        description: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        user_id: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> None:
        """Log equipment changes to the equipment_log table"""
        log = EquipmentLog(
            equipment_id=equipment_id,
            log_type=log_type,
            old_value=old_value,
            new_value=new_value,
            description=description,
            latitude=latitude,
            longitude=longitude,
            created_by=user_id,
        )
        self.db.add(log)

    # ==================== Location Helpers ====================

    async def get_location_info(self, location_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """Get location info dictionary for logging"""
        if not location_id:
            return None

        result = await self.db.execute(
            select(Location).where(Location.id == location_id)
        )
        location = result.scalar_one_or_none()

        if not location:
            return None

        return {
            "id": location.id,
            "name": location.name,
            "type": location.location_type.value if location.location_type else None
        }

    def build_status_log_json(
        self,
        status: str,
        location_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build JSON string for status change logging"""
        return json.dumps({
            "status": status,
            "location": location_info
        }, ensure_ascii=False)

    # ==================== Parent-Child Sync ====================

    async def sync_children_with_parent(
        self,
        parent_id: int,
        user_id: int,
        sync_status: bool = True,
        sync_location: bool = True,
        sync_project: bool = True,
        notes: Optional[str] = None
    ) -> int:
        """
        Sync all child equipment with parent's status, location, and project.
        Returns the number of children synced.
        """
        # Get parent equipment
        parent_result = await self.db.execute(
            select(Equipment).where(Equipment.id == parent_id)
        )
        parent = parent_result.scalar_one_or_none()

        if not parent:
            return 0

        # Get all active children
        children_result = await self.db.execute(
            select(Equipment).where(
                Equipment.parent_equipment_id == parent_id,
                Equipment.is_active == True
            )
        )
        children = children_result.scalars().all()

        if not children:
            return 0

        synced_count = 0

        # Get parent's location info once
        parent_location_info = await self.get_location_info(parent.current_location_id)

        # Sync each child
        for child in children:
            sync_changes = []
            old_status = child.status
            old_location = child.current_location_id

            if sync_status and child.status.value != parent.status.value:
                child.status = parent.status
                sync_changes.append(f"status: {old_status.value} → {parent.status.value}")
                logger.debug(f"[SYNC] Updated {child.asset_code} status")

            if sync_location and child.current_location_id != parent.current_location_id:
                child.current_location_id = parent.current_location_id
                sync_changes.append(f"location_id: {old_location} → {parent.current_location_id}")
                logger.debug(f"[SYNC] Updated {child.asset_code} location")

            if sync_project and child.project_id != parent.project_id:
                old_project = child.project_id
                child.project_id = parent.project_id
                sync_changes.append(f"project_id: {old_project} → {parent.project_id}")
                logger.debug(f"[SYNC] Updated {child.asset_code} project")

            # Log the sync if there were changes
            if sync_changes:
                synced_count += 1
                description = f"Auto-synced with parent {parent.asset_code}"
                if notes:
                    description += f" - {notes}"

                # Build old/new value JSON
                child_old_location_info = {"id": old_location, "name": None, "type": None} if old_location else None

                old_value_json = self.build_status_log_json(
                    old_status.value if hasattr(old_status, 'value') else str(old_status),
                    child_old_location_info
                )
                new_value_json = self.build_status_log_json(
                    parent.status.value if hasattr(parent.status, 'value') else str(parent.status),
                    parent_location_info
                )

                await self.log_equipment_change(
                    equipment_id=child.id,
                    log_type=EquipmentLogType.STATUS_CHANGE,
                    description=description,
                    old_value=old_value_json,
                    new_value=new_value_json,
                    user_id=user_id,
                )

        return synced_count

    # ==================== Equipment Query ====================

    async def get_equipment_by_id(
        self,
        equipment_id: int,
        include_relations: bool = True
    ) -> Optional[Equipment]:
        """Get equipment by ID with optional relations"""
        query = select(Equipment).where(
            Equipment.id == equipment_id,
            Equipment.is_active == True
        )

        if include_relations:
            query = query.options(
                selectinload(Equipment.current_location),
                selectinload(Equipment.project),
                selectinload(Equipment.parent_equipment),
                selectinload(Equipment.children)
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_equipment_by_asset_code(
        self,
        asset_code: str,
        include_relations: bool = True
    ) -> Optional[Equipment]:
        """Get equipment by asset code with optional relations"""
        query = select(Equipment).where(
            Equipment.asset_code == asset_code,
            Equipment.is_active == True
        )

        if include_relations:
            query = query.options(
                selectinload(Equipment.current_location),
                selectinload(Equipment.project),
                selectinload(Equipment.parent_equipment),
                selectinload(Equipment.children)
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_children(self, parent_id: int) -> List[Equipment]:
        """Get all active children of a parent equipment"""
        result = await self.db.execute(
            select(Equipment)
            .where(
                Equipment.parent_equipment_id == parent_id,
                Equipment.is_active == True
            )
            .options(selectinload(Equipment.current_location))
        )
        return list(result.scalars().all())

    # ==================== Status Change Operations ====================

    async def change_status(
        self,
        equipment: Equipment,
        new_status: EquipmentStatus,
        user_id: int,
        description: str,
        new_location_id: Optional[int] = None,
        new_project_id: Optional[int] = None,
        sync_children: bool = True,
        notes: Optional[str] = None,
    ) -> Equipment:
        """
        Change equipment status with logging and optional child sync.
        Returns the updated equipment.
        """
        old_status = equipment.status
        old_location_id = equipment.current_location_id

        # Get location info for logging
        old_location_info = await self.get_location_info(old_location_id)

        # Update equipment
        equipment.status = new_status

        if new_location_id is not None:
            equipment.current_location_id = new_location_id

        if new_project_id is not None:
            equipment.project_id = new_project_id

        # Get new location info
        new_location_info = await self.get_location_info(equipment.current_location_id)

        # Log the change
        old_value_json = self.build_status_log_json(old_status.value, old_location_info)
        new_value_json = self.build_status_log_json(new_status.value, new_location_info)

        await self.log_equipment_change(
            equipment_id=equipment.id,
            log_type=EquipmentLogType.STATUS_CHANGE,
            description=description,
            old_value=old_value_json,
            new_value=new_value_json,
            user_id=user_id,
        )

        # Sync children if requested
        if sync_children:
            await self.sync_children_with_parent(
                parent_id=equipment.id,
                user_id=user_id,
                notes=notes or description
            )

        return equipment

    # ==================== Maintenance Operations ====================

    async def add_maintenance_record(
        self,
        equipment: Equipment,
        user_id: int,
        last_maintenance_date: Optional[str] = None,
        next_maintenance_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Equipment:
        """Add maintenance record to equipment"""
        old_last = equipment.last_maintenance_date
        old_next = equipment.next_maintenance_date

        if last_maintenance_date:
            equipment.last_maintenance_date = datetime.strptime(
                last_maintenance_date, "%Y-%m-%d"
            ).date()

        if next_maintenance_date:
            equipment.next_maintenance_date = datetime.strptime(
                next_maintenance_date, "%Y-%m-%d"
            ).date()

        if notes:
            equipment.maintenance_notes = notes

        # Log the change
        old_value = json.dumps({
            "last_maintenance_date": str(old_last) if old_last else None,
            "next_maintenance_date": str(old_next) if old_next else None,
        }, ensure_ascii=False)

        new_value = json.dumps({
            "last_maintenance_date": str(equipment.last_maintenance_date) if equipment.last_maintenance_date else None,
            "next_maintenance_date": str(equipment.next_maintenance_date) if equipment.next_maintenance_date else None,
        }, ensure_ascii=False)

        await self.log_equipment_change(
            equipment_id=equipment.id,
            log_type=EquipmentLogType.MAINTENANCE,
            description=notes or "Maintenance record updated",
            old_value=old_value,
            new_value=new_value,
            user_id=user_id,
        )

        return equipment

    # ==================== Note Operations ====================

    async def add_note(
        self,
        equipment: Equipment,
        user_id: int,
        note: str,
    ) -> None:
        """Add a note to equipment log"""
        await self.log_equipment_change(
            equipment_id=equipment.id,
            log_type=EquipmentLogType.NOTE,
            description=note,
            user_id=user_id,
        )

    # ==================== Soft Delete ====================

    async def soft_delete(
        self,
        equipment: Equipment,
        user_id: int,
    ) -> None:
        """Soft delete equipment and its children"""
        equipment.is_active = False

        # Log the deletion
        await self.log_equipment_change(
            equipment_id=equipment.id,
            log_type=EquipmentLogType.UPDATED,
            description="Equipment deactivated (soft delete)",
            old_value=json.dumps({"is_active": True}),
            new_value=json.dumps({"is_active": False}),
            user_id=user_id,
        )

        # Also deactivate children
        children = await self.get_children(equipment.id)
        for child in children:
            child.is_active = False
            await self.log_equipment_change(
                equipment_id=child.id,
                log_type=EquipmentLogType.UPDATED,
                description=f"Deactivated with parent {equipment.asset_code}",
                old_value=json.dumps({"is_active": True}),
                new_value=json.dumps({"is_active": False}),
                user_id=user_id,
            )

    # ==================== Detach from Parent ====================

    async def detach_from_parent(
        self,
        equipment: Equipment,
        user_id: int,
        reason: Optional[str] = None,
    ) -> Equipment:
        """Detach equipment from its parent"""
        if not equipment.parent_equipment_id:
            return equipment

        old_parent_id = equipment.parent_equipment_id

        # Get parent info for logging
        parent_result = await self.db.execute(
            select(Equipment).where(Equipment.id == old_parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        parent_asset_code = parent.asset_code if parent else "Unknown"

        # Detach
        equipment.parent_equipment_id = None

        # Log the change
        description = f"Detached from parent {parent_asset_code}"
        if reason:
            description += f" - {reason}"

        await self.log_equipment_change(
            equipment_id=equipment.id,
            log_type=EquipmentLogType.UPDATED,
            description=description,
            old_value=json.dumps({
                "parent_equipment_id": old_parent_id,
                "parent_asset_code": parent_asset_code
            }),
            new_value=json.dumps({
                "parent_equipment_id": None,
                "parent_asset_code": None
            }),
            user_id=user_id,
        )

        return equipment
