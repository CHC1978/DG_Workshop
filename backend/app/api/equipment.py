"""Equipment management API endpoints"""
import json
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager, require_admin, require_operator
from app.models.user import User
from app.models.equipment import Equipment, EquipmentStatus, EquipmentCategory
from app.models.equipment_log import EquipmentLog, EquipmentLogType
from app.models.location import Location
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
    EquipmentDetailResponse,
    EquipmentLogResponse,
    EquipmentLogUpdateRequest,
    MaintenanceRecordRequest,
    DetachFromParentRequest,
    GroupMoveRequest,
    SyncChildrenStatusRequest,
)
from app.utils.asset_code import generate_asset_code, generate_asset_code_v2, generate_qr_code_url, clean_model_code
from app.services.equipment_service import EquipmentService

router = APIRouter(prefix="/equipment", tags=["Equipment"])


# ==================== Helper Functions (delegating to Service) ====================

async def log_equipment_change(
    db: AsyncSession,
    equipment_id: int,
    log_type: EquipmentLogType,
    description: str,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    user_id: Optional[int] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
):
    """Helper function to log equipment changes - delegates to EquipmentService"""
    service = EquipmentService(db)
    await service.log_equipment_change(
        equipment_id=equipment_id,
        log_type=log_type,
        description=description,
        old_value=old_value,
        new_value=new_value,
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
    )


async def sync_children_with_parent(
    db: AsyncSession,
    parent_id: int,
    user_id: int,
    sync_status: bool = True,
    sync_location: bool = True,
    sync_project: bool = True,
    notes: Optional[str] = None
) -> int:
    """
    Helper function to sync all child equipment with parent's status, location, and project.
    Delegates to EquipmentService.
    Returns the number of children synced.
    """
    service = EquipmentService(db)
    return await service.sync_children_with_parent(
        parent_id=parent_id,
        user_id=user_id,
        sync_status=sync_status,
        sync_location=sync_location,
        sync_project=sync_project,
        notes=notes,
    )


# ==================== CRUD Operations ====================

@router.get("", response_model=EquipmentListResponse)
async def list_equipment(
    skip: int = 0,
    limit: int = 100,
    category: Optional[EquipmentCategory] = None,
    status: Optional[EquipmentStatus] = None,
    location_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all equipment with filtering and pagination
    Only returns parent equipment (equipment with parent_equipment_id = NULL)
    Sub-components are accessed via /equipment/{id}/children endpoint
    """
    from sqlalchemy.orm import selectinload
    from app.models.location import Location
    from app.models.project import Project

    # Only show parent equipment (not sub-components)
    query = select(Equipment).where(
        Equipment.is_active == True,
        Equipment.parent_equipment_id == None
    )

    # Apply filters
    if category:
        query = query.where(Equipment.category == category)
    if status:
        query = query.where(Equipment.status == status)
    if location_id:
        query = query.where(Equipment.current_location_id == location_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Equipment.asset_code.like(search_pattern),
                Equipment.manufacturer.like(search_pattern),
                Equipment.model.like(search_pattern),
                Equipment.serial_number.like(search_pattern),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results with eager loading
    query = (
        query
        .options(selectinload(Equipment.current_location))
        .options(selectinload(Equipment.project))
        .options(selectinload(Equipment.assigned_user))
        .offset(skip)
        .limit(limit)
        .order_by(Equipment.created_at.desc())
    )
    result = await db.execute(query)
    equipment_list = result.scalars().all()

    # Build response with location, project, and children count
    equipments_response = []
    for eq in equipment_list:
        eq_dict = EquipmentResponse.model_validate(eq).model_dump()

        # Add location info
        if eq.current_location:
            eq_dict['current_location_name'] = eq.current_location.name
            eq_dict['current_location_type'] = eq.current_location.location_type.value

        # Add project info
        if eq.project:
            eq_dict['project_code'] = eq.project.code
            eq_dict['project_name'] = eq.project.name

        # Add assigned user info
        if eq.assigned_user:
            eq_dict['assigned_user_name'] = eq.assigned_user.full_name

        # Count children
        children_result = await db.execute(
            select(func.count(Equipment.id))
            .where(Equipment.parent_equipment_id == eq.id)
            .where(Equipment.is_active == True)
        )
        eq_dict['children_count'] = children_result.scalar() or 0

        equipments_response.append(EquipmentResponse(**eq_dict))

    return EquipmentListResponse(
        equipments=equipments_response,
        total=total
    )


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    equipment_data: EquipmentCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new equipment (Manager+ only)
    Auto-generates asset code and QR code using new v2 format

    Asset Code format:
    - With serial number: {CATEGORY}-{MODEL_CODE}-SN{SERIAL}
    - Without serial number: {CATEGORY}-{MODEL_CODE}-{SEQ:04d}
    """
    # Determine model_code
    model_code = equipment_data.model_code
    if not model_code:
        # Auto-generate from model name
        model_code = clean_model_code(equipment_data.model)

    # Generate asset code using v2 format
    asset_code = await generate_asset_code_v2(
        equipment_data.category,
        model_code,
        db,
        equipment_data.serial_number
    )

    # Generate QR code URL
    qr_code = generate_qr_code_url(asset_code)

    # Create equipment using all fields
    equipment_dict = equipment_data.model_dump()
    equipment_dict.update({
        'asset_code': asset_code,
        'qr_code': qr_code,
        'model_code': model_code,
        'status': EquipmentStatus.ORDERING,
        'is_active': True,
    })

    new_equipment = Equipment(**equipment_dict)

    db.add(new_equipment)
    await db.flush()  # Get ID before logging

    # Log creation with JSON format
    await log_equipment_change(
        db=db,
        equipment_id=new_equipment.id,
        log_type=EquipmentLogType.CREATED,
        description=f"Equipment created: {asset_code}",
        new_value=json.dumps({
            "status": EquipmentStatus.ORDERING.value,
            "location": None
        }, ensure_ascii=False),
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(new_equipment)

    return EquipmentResponse.model_validate(new_equipment)


@router.get("/by-qr/{asset_code}", response_model=EquipmentDetailResponse)
async def get_equipment_by_qr(
    asset_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get equipment by asset code (QR code scan)
    """
    result = await db.execute(
        select(Equipment).where(Equipment.asset_code == asset_code)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment not found: {asset_code}",
        )

    return EquipmentDetailResponse.model_validate(equipment)


@router.get("/{equipment_id}", response_model=EquipmentDetailResponse)
async def get_equipment(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get equipment by ID with parent, project, and children info
    """
    from sqlalchemy.orm import selectinload
    from app.models.location import Location
    from app.models.project import Project

    result = await db.execute(
        select(Equipment)
        .options(selectinload(Equipment.current_location))
        .options(selectinload(Equipment.project))
        .options(selectinload(Equipment.parent))
        .options(selectinload(Equipment.assigned_user))
        .where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Build response with additional info
    eq_dict = EquipmentDetailResponse.model_validate(equipment).model_dump()

    # Add location info
    if equipment.current_location:
        eq_dict['current_location_name'] = equipment.current_location.name
        eq_dict['current_location_type'] = equipment.current_location.location_type.value

    # Add project info
    if equipment.project:
        eq_dict['project_code'] = equipment.project.code
        eq_dict['project_name'] = equipment.project.name

    # Add assigned user info
    if equipment.assigned_user:
        eq_dict['assigned_user_name'] = equipment.assigned_user.full_name

    # Add parent equipment info
    if equipment.parent:
        eq_dict['parent_asset_code'] = equipment.parent.asset_code
        eq_dict['parent_model'] = equipment.parent.model

    # Count children
    children_result = await db.execute(
        select(func.count(Equipment.id))
        .where(Equipment.parent_equipment_id == equipment_id)
        .where(Equipment.is_active == True)
    )
    eq_dict['children_count'] = children_result.scalar() or 0

    return EquipmentDetailResponse(**eq_dict)


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update equipment (Manager+ only)
    """
    logger.debug(f"[UPDATE API] ===== UPDATE EQUIPMENT REQUEST =====")
    logger.debug(f"[UPDATE API] Equipment ID: {equipment_id}")
    logger.debug(f"[UPDATE API] User ID: {current_user.id}")

    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        logger.debug(f"[UPDATE API] ERROR: Equipment {equipment_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    logger.debug(f"[UPDATE API] Current equipment: {equipment.asset_code}")
    logger.debug(f"[UPDATE API] Current status: {equipment.status.value}")
    logger.debug(f"[UPDATE API] Current location: {equipment.current_location_id}")
    logger.debug(f"[UPDATE API] Current project: {equipment.project_id}")
    logger.debug(f"[UPDATE API] Current parent_id: {equipment.parent_equipment_id}")

    # Track changes for logging
    changes = []
    parent_changed = False
    old_parent_id = equipment.parent_equipment_id
    new_parent_id = None

    # Store old values for JSON log
    old_status = equipment.status
    old_location_id = equipment.current_location_id

    # Update fields
    update_data = equipment_data.model_dump(exclude_unset=True)
    logger.debug(f"[UPDATE API] Update data received: {update_data}")
    for field, value in update_data.items():
        if hasattr(equipment, field):
            old_value = getattr(equipment, field)
            if old_value != value:
                changes.append(f"{field}: {old_value} -> {value}")
                setattr(equipment, field, value)

                # Track parent_equipment_id change
                if field == 'parent_equipment_id':
                    parent_changed = True
                    new_parent_id = value

    # Log changes
    if changes:
        # Check if status or location changed for JSON format log
        status_changed = 'status' in update_data
        location_changed = 'current_location_id' in update_data

        # Special log for parent equipment attachment/detachment
        if parent_changed:
            if old_parent_id is None and new_parent_id is not None:
                # Attaching to parent - sync status, location, and project
                parent_result = await db.execute(
                    select(Equipment).where(Equipment.id == new_parent_id)
                )
                parent_equipment = parent_result.scalar_one_or_none()
                if parent_equipment:
                    # Sync child's status, location, and project with parent
                    sync_changes = []

                    logger.debug(f"[ATTACH SYNC] Child equipment: {equipment.asset_code}")
                    logger.debug(f"[ATTACH SYNC] Parent equipment: {parent_equipment.asset_code}")

                    # Sync status
                    if equipment.status.value != parent_equipment.status.value:
                        old_sync_status = equipment.status
                        equipment.status = parent_equipment.status
                        sync_changes.append(f"status: {old_sync_status.value} → {parent_equipment.status.value}")

                    # Sync location
                    if equipment.current_location_id != parent_equipment.current_location_id:
                        old_location = equipment.current_location_id
                        equipment.current_location_id = parent_equipment.current_location_id
                        sync_changes.append(f"location_id: {old_location} → {parent_equipment.current_location_id}")

                    # Sync project
                    if equipment.project_id != parent_equipment.project_id:
                        old_project = equipment.project_id
                        equipment.project_id = parent_equipment.project_id
                        sync_changes.append(f"project_id: {old_project} → {parent_equipment.project_id}")

                    # Log attachment with sync details
                    sync_detail = f" (Synced: {', '.join(sync_changes)})" if sync_changes else ""
                    await log_equipment_change(
                        db=db,
                        equipment_id=equipment.id,
                        log_type=EquipmentLogType.UPDATED,
                        description=f"Attached as child component to {parent_equipment.asset_code}{sync_detail}",
                        old_value=f"parent_id: None",
                        new_value=f"parent_id: {new_parent_id} ({parent_equipment.asset_code})",
                        user_id=current_user.id,
                    )
            elif old_parent_id is not None and new_parent_id is None:
                # Detaching from parent
                await log_equipment_change(
                    db=db,
                    equipment_id=equipment.id,
                    log_type=EquipmentLogType.UPDATED,
                    description=f"Detached from parent equipment",
                    old_value=f"parent_id: {old_parent_id}",
                    new_value=f"parent_id: None",
                    user_id=current_user.id,
                )

        # Regular update log with JSON format for status/location changes
        if not parent_changed or len(changes) > 1:
            if status_changed or location_changed:
                # Get old location info
                old_location_info = None
                if old_location_id:
                    old_loc_result = await db.execute(
                        select(Location).where(Location.id == old_location_id)
                    )
                    old_location = old_loc_result.scalar_one_or_none()
                    if old_location:
                        old_location_info = {
                            "id": old_location.id,
                            "name": old_location.name,
                            "type": old_location.location_type.value if old_location.location_type else None
                        }

                # Get new location info
                new_location_info = None
                if equipment.current_location_id:
                    new_loc_result = await db.execute(
                        select(Location).where(Location.id == equipment.current_location_id)
                    )
                    new_location = new_loc_result.scalar_one_or_none()
                    if new_location:
                        new_location_info = {
                            "id": new_location.id,
                            "name": new_location.name,
                            "type": new_location.location_type.value if new_location.location_type else None
                        }

                # Build JSON for old/new values
                old_value_json = json.dumps({
                    "status": old_status.value if hasattr(old_status, 'value') else str(old_status),
                    "location": old_location_info
                }, ensure_ascii=False)

                new_value_json = json.dumps({
                    "status": equipment.status.value if hasattr(equipment.status, 'value') else str(equipment.status),
                    "location": new_location_info
                }, ensure_ascii=False)

                # Build description
                description = "Equipment updated"
                if new_location_info:
                    description = f"Equipment updated - moved to {new_location_info['name']}"

                await log_equipment_change(
                    db=db,
                    equipment_id=equipment.id,
                    log_type=EquipmentLogType.UPDATED,
                    description=description,
                    old_value=old_value_json,
                    new_value=new_value_json,
                    user_id=current_user.id,
                )
            else:
                # Non status/location changes - use old format
                await log_equipment_change(
                    db=db,
                    equipment_id=equipment.id,
                    log_type=EquipmentLogType.UPDATED,
                    description=f"Equipment updated",
                    old_value="; ".join(changes[:5]),  # Limit to first 5 changes
                    user_id=current_user.id,
                )

    # If this equipment is a parent and its status/location/project changed,
    # sync all children to match
    status_changed = 'status' in [c.split(':')[0] for c in changes]
    location_changed = 'current_location_id' in [c.split(':')[0] for c in changes]
    project_changed = 'project_id' in [c.split(':')[0] for c in changes]

    if (status_changed or location_changed or project_changed):
        # Check if this equipment has children
        children_check = await db.execute(
            select(func.count(Equipment.id))
            .where(Equipment.parent_equipment_id == equipment_id)
            .where(Equipment.is_active == True)
        )
        children_count = children_check.scalar() or 0

        if children_count > 0:
            # Flush changes before syncing children (required because autoflush=False)
            await db.flush()

            # Sync children with parent
            await sync_children_with_parent(
                db=db,
                parent_id=equipment_id,
                user_id=current_user.id,
                sync_status=status_changed,
                sync_location=location_changed,
                sync_project=project_changed,
                notes="Parent equipment updated"
            )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (deactivate) equipment (Admin only)
    Uses soft delete by setting is_active to False
    """
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Soft delete
    equipment.is_active = False

    # Log deletion with JSON format
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=f"Equipment deactivated",
        old_value=json.dumps({"is_active": True}, ensure_ascii=False),
        new_value=json.dumps({"is_active": False}, ensure_ascii=False),
        user_id=current_user.id,
    )

    await db.commit()


# ==================== Equipment Logs ====================

@router.get("/{equipment_id}/logs", response_model=list[EquipmentLogResponse])
async def get_equipment_logs(
    equipment_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get equipment change logs with user information
    """
    # Verify equipment exists
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Get logs with user join (creator and editor)
    from sqlalchemy.orm import aliased
    Creator = aliased(User)
    Editor = aliased(User)

    query = (
        select(EquipmentLog, Creator, Editor)
        .outerjoin(Creator, EquipmentLog.created_by == Creator.id)
        .outerjoin(Editor, EquipmentLog.edited_by == Editor.id)
        .where(EquipmentLog.equipment_id == equipment_id)
        .order_by(EquipmentLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    log_rows = result.all()

    # Get current equipment location and project info
    from app.models.location import Location
    from app.models.project import Project
    from app.models.log_attachment import LogAttachment

    current_location = None
    current_project = None

    if equipment.current_location_id:
        loc_result = await db.execute(
            select(Location).where(Location.id == equipment.current_location_id)
        )
        current_location = loc_result.scalar_one_or_none()

    if equipment.project_id:
        proj_result = await db.execute(
            select(Project).where(Project.id == equipment.project_id)
        )
        current_project = proj_result.scalar_one_or_none()

    # Get all log IDs to fetch attachments
    log_ids = [log.id for log, _, _ in log_rows]

    # Fetch all attachments for these logs in one query
    attachments_result = await db.execute(
        select(LogAttachment).where(LogAttachment.equipment_log_id.in_(log_ids))
    )
    all_attachments = attachments_result.scalars().all()

    # Group attachments by log_id
    attachments_by_log: dict[int, list] = {}
    for att in all_attachments:
        if att.equipment_log_id not in attachments_by_log:
            attachments_by_log[att.equipment_log_id] = []
        attachments_by_log[att.equipment_log_id].append({
            "id": att.id,
            "file_url": att.file_url,
            "file_name": att.file_name,
            "file_type": att.file_type.value,
            "file_size": att.file_size
        })

    # Build response with usernames and current location/project
    responses = []
    for log, creator, editor in log_rows:
        # Build log dict manually to avoid lazy loading issues
        log_dict = {
            "id": log.id,
            "equipment_id": log.equipment_id,
            "log_type": log.log_type.value if hasattr(log.log_type, 'value') else log.log_type,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "description": log.description,
            "latitude": log.latitude,
            "longitude": log.longitude,
            "created_at": log.created_at,
            "created_by": log.created_by,
            "created_by_username": creator.username if creator else None,
            "edited_at": log.edited_at,
            "edited_by": log.edited_by,
            "edited_by_username": editor.username if editor else None,
            "edit_count": log.edit_count,
            "is_edited": log.edit_count > 0,
        }

        # Add current equipment location and project info
        if current_location:
            log_dict['current_location_name'] = current_location.name
            log_dict['current_location_type'] = current_location.location_type.value
        if current_project:
            log_dict['project_code'] = current_project.code
            log_dict['project_name'] = current_project.name

        # Add attachments
        log_attachments = attachments_by_log.get(log.id, [])
        log_dict['attachment_count'] = len(log_attachments)
        log_dict['attachments'] = log_attachments

        responses.append(EquipmentLogResponse(**log_dict))

    return responses


@router.put("/{equipment_id}/logs/{log_id}", response_model=EquipmentLogResponse)
async def update_equipment_log(
    equipment_id: int,
    log_id: int,
    log_update: EquipmentLogUpdateRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update equipment log (Manager+ only)

    Only allows editing:
    - description
    - latitude
    - longitude

    Cannot edit:
    - log_type
    - old_value
    - new_value

    Edit history is tracked in the log itself.
    """
    # Verify equipment exists
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    # Get log with creator and editor
    from sqlalchemy.orm import aliased
    Creator = aliased(User)
    Editor = aliased(User)

    log_result = await db.execute(
        select(EquipmentLog, Creator, Editor)
        .outerjoin(Creator, EquipmentLog.created_by == Creator.id)
        .outerjoin(Editor, EquipmentLog.edited_by == Editor.id)
        .where(
            EquipmentLog.id == log_id,
            EquipmentLog.equipment_id == equipment_id
        )
    )
    row = log_result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )

    log, creator, editor = row

    # First edit: save original values
    if log.edit_count == 0:
        log.original_description = log.description
        log.original_latitude = log.latitude
        log.original_longitude = log.longitude

    # Update editable fields
    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(log, field):
            setattr(log, field, value)

    # Update edit tracking
    log.edited_at = datetime.utcnow()
    log.edited_by = current_user.id
    log.edit_count += 1

    await db.commit()
    await db.refresh(log)

    # Build response with usernames
    log_dict = EquipmentLogResponse.model_validate(log).model_dump()
    log_dict['created_by_username'] = creator.username if creator else None
    log_dict['edited_by_username'] = current_user.username
    log_dict['is_edited'] = log.edit_count > 0

    return EquipmentLogResponse(**log_dict)


@router.delete("/{equipment_id}/logs")
async def clear_equipment_logs(
    equipment_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear all logs for an equipment (Admin only)
    """
    # Verify equipment exists
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    # Count logs to delete
    count_result = await db.execute(
        select(func.count(EquipmentLog.id)).where(EquipmentLog.equipment_id == equipment_id)
    )
    count = count_result.scalar()

    # Delete all logs for this equipment
    from sqlalchemy import delete
    await db.execute(
        delete(EquipmentLog).where(EquipmentLog.equipment_id == equipment_id)
    )

    await db.commit()

    return {"message": f"Deleted {count} logs for equipment {equipment.asset_code}", "deleted_count": count}


# ==================== Status Change Operations ====================

@router.post("/{equipment_id}/deploy", response_model=EquipmentResponse)
async def deploy_equipment(
    equipment_id: int,
    location_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Deploy equipment to a location (Operator+ only)
    Changes status to DEPLOYED
    """
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Check if equipment can be deployed
    # Allow: IN_STOCK, ORDERING, DEPLOYED (direct transfer without return)
    allowed_statuses = [EquipmentStatus.IN_STOCK, EquipmentStatus.ORDERING, EquipmentStatus.DEPLOYED]
    if equipment.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deploy equipment with status: {equipment.status.value}",
        )

    # Get target location name
    loc_result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    target_location = loc_result.scalar_one_or_none()
    if not target_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    # Update status and location
    old_status = equipment.status
    old_location_id = equipment.current_location_id

    # Get old location info if exists
    old_location_info = None
    if old_location_id:
        old_loc_result = await db.execute(
            select(Location).where(Location.id == old_location_id)
        )
        old_location = old_loc_result.scalar_one_or_none()
        if old_location:
            old_location_info = {
                "id": old_location.id,
                "name": old_location.name,
                "type": old_location.location_type.value if old_location.location_type else None
            }

    equipment.status = EquipmentStatus.DEPLOYED
    equipment.current_location_id = location_id

    # Build structured JSON for old/new values
    old_value_json = json.dumps({
        "status": old_status.value,
        "location": old_location_info
    }, ensure_ascii=False)

    new_value_json = json.dumps({
        "status": EquipmentStatus.DEPLOYED.value,
        "location": {
            "id": target_location.id,
            "name": target_location.name,
            "type": target_location.location_type.value if target_location.location_type else None
        }
    }, ensure_ascii=False)

    # Log the deployment with structured JSON
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=notes or f"Equipment deployed to {target_location.name}",
        old_value=old_value_json,
        new_value=new_value_json,
        user_id=current_user.id,
    )

    # Flush changes before syncing children (required because autoflush=False)
    await db.flush()

    # Sync children with parent's new status and location
    await sync_children_with_parent(
        db=db,
        parent_id=equipment_id,
        user_id=current_user.id,
        sync_status=True,
        sync_location=True,
        sync_project=False,
        notes="Parent deployed"
    )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.post("/{equipment_id}/return", response_model=EquipmentResponse)
async def return_equipment(
    equipment_id: int,
    location_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Return equipment to warehouse (Operator+ only)
    Changes status to IN_STOCK
    """
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Get target location name
    loc_result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    target_location = loc_result.scalar_one_or_none()
    if not target_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    # Update status and location
    old_status = equipment.status
    old_location_id = equipment.current_location_id

    # Get old location info if exists
    old_location_info = None
    if old_location_id:
        old_loc_result = await db.execute(
            select(Location).where(Location.id == old_location_id)
        )
        old_location = old_loc_result.scalar_one_or_none()
        if old_location:
            old_location_info = {
                "id": old_location.id,
                "name": old_location.name,
                "type": old_location.location_type.value if old_location.location_type else None
            }

    equipment.status = EquipmentStatus.IN_STOCK
    equipment.current_location_id = location_id

    # Build structured JSON for old/new values
    old_value_json = json.dumps({
        "status": old_status.value,
        "location": old_location_info
    }, ensure_ascii=False)

    new_value_json = json.dumps({
        "status": EquipmentStatus.IN_STOCK.value,
        "location": {
            "id": target_location.id,
            "name": target_location.name,
            "type": target_location.location_type.value if target_location.location_type else None
        }
    }, ensure_ascii=False)

    # Log the return with structured JSON
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=notes or f"Equipment returned to {target_location.name}",
        old_value=old_value_json,
        new_value=new_value_json,
        user_id=current_user.id,
    )

    # Flush changes before syncing children (required because autoflush=False)
    await db.flush()

    # Sync children with parent's new status and location
    await sync_children_with_parent(
        db=db,
        parent_id=equipment_id,
        user_id=current_user.id,
        sync_status=True,
        sync_location=True,
        sync_project=False,
        notes="Parent returned to stock"
    )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.post("/{equipment_id}/repair", response_model=EquipmentResponse)
async def send_to_repair(
    equipment_id: int,
    location_id: Optional[int] = None,
    expected_return_date: Optional[str] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Send equipment to repair (Operator+ only)
    Changes status to REPAIR, optionally sets location
    """
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Verify location if provided
    target_location = None
    if location_id:
        loc_result = await db.execute(
            select(Location).where(Location.id == location_id)
        )
        target_location = loc_result.scalar_one_or_none()
        if not target_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )

    # Update status
    old_status = equipment.status
    old_location_id = equipment.current_location_id
    equipment.status = EquipmentStatus.REPAIR

    # Get old location info
    old_location_info = None
    if old_location_id:
        old_loc_result = await db.execute(
            select(Location).where(Location.id == old_location_id)
        )
        old_location = old_loc_result.scalar_one_or_none()
        if old_location:
            old_location_info = {
                "id": old_location.id,
                "name": old_location.name,
                "type": old_location.location_type.value if old_location.location_type else None
            }

    # Update location if provided
    if location_id:
        equipment.current_location_id = location_id

    # Build description with details
    description_parts = [notes or "Equipment sent to repair"]
    if target_location:
        description_parts.append(f"Location: {target_location.name}")
    if expected_return_date:
        description_parts.append(f"Expected return: {expected_return_date}")

    # Build structured JSON for old/new values
    old_value_json = json.dumps({
        "status": old_status.value,
        "location": old_location_info
    }, ensure_ascii=False)

    new_location_info = None
    if target_location:
        new_location_info = {
            "id": target_location.id,
            "name": target_location.name,
            "type": target_location.location_type.value if target_location.location_type else None
        }

    new_value_json = json.dumps({
        "status": EquipmentStatus.REPAIR.value,
        "location": new_location_info
    }, ensure_ascii=False)

    # Log the repair with structured JSON
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.MAINTENANCE,
        description=" | ".join(description_parts),
        old_value=old_value_json,
        new_value=new_value_json,
        user_id=current_user.id,
    )

    # Flush changes before syncing children (required because autoflush=False)
    await db.flush()

    # Sync children with parent's new status
    await sync_children_with_parent(
        db=db,
        parent_id=equipment_id,
        user_id=current_user.id,
        sync_status=True,
        sync_location=location_id is not None,
        sync_project=False,
        notes="Parent sent to repair"
    )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.post("/{equipment_id}/send-to-calibration", response_model=EquipmentResponse)
async def send_to_calibration(
    equipment_id: int,
    location_id: Optional[int] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Send equipment to calibration (Operator+ only)
    Changes status to CALIBRATING, optionally sets location
    """
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Verify location if provided
    target_location = None
    if location_id:
        loc_result = await db.execute(
            select(Location).where(Location.id == location_id)
        )
        target_location = loc_result.scalar_one_or_none()
        if not target_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )

    # Update status
    old_status = equipment.status
    old_location_id = equipment.current_location_id
    equipment.status = EquipmentStatus.CALIBRATING

    # Get old location info
    old_location_info = None
    if old_location_id:
        old_loc_result = await db.execute(
            select(Location).where(Location.id == old_location_id)
        )
        old_location = old_loc_result.scalar_one_or_none()
        if old_location:
            old_location_info = {
                "id": old_location.id,
                "name": old_location.name,
                "type": old_location.location_type.value if old_location.location_type else None
            }

    # Update location if provided
    if location_id:
        equipment.current_location_id = location_id

    # Build description with details
    description_parts = [notes or "Equipment sent to calibration"]
    if target_location:
        description_parts.append(f"Location: {target_location.name}")
    if equipment.calibration_due:
        description_parts.append(f"Cal Due: {equipment.calibration_due.strftime('%Y-%m-%d')}")

    # Build structured JSON for old/new values
    old_value_json = json.dumps({
        "status": old_status.value,
        "location": old_location_info
    }, ensure_ascii=False)

    new_location_info = None
    if target_location:
        new_location_info = {
            "id": target_location.id,
            "name": target_location.name,
            "type": target_location.location_type.value if target_location.location_type else None
        }

    new_value_json = json.dumps({
        "status": EquipmentStatus.CALIBRATING.value,
        "location": new_location_info
    }, ensure_ascii=False)

    # Log the calibration send with structured JSON
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.CALIBRATION,
        description=" | ".join(description_parts),
        old_value=old_value_json,
        new_value=new_value_json,
        user_id=current_user.id,
    )

    # Flush changes before syncing children (required because autoflush=False)
    await db.flush()

    # Sync children with parent's new status
    await sync_children_with_parent(
        db=db,
        parent_id=equipment_id,
        user_id=current_user.id,
        sync_status=True,
        sync_location=location_id is not None,
        sync_project=False,
        notes="Parent sent to calibration"
    )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.post("/{equipment_id}/note", response_model=dict)
async def add_equipment_note(
    equipment_id: int,
    note: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a note to equipment log
    """
    # Verify equipment exists
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Add note to log
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.NOTE,
        description=note,
        user_id=current_user.id,
        latitude=latitude,
        longitude=longitude,
    )

    await db.commit()

    return {"message": "Note added successfully"}


@router.post("/{equipment_id}/maintenance", response_model=dict)
async def add_maintenance_record(
    equipment_id: int,
    request: MaintenanceRecordRequest,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Add maintenance record to equipment (Operator+ only)
    Updates equipment maintenance fields and creates a MAINTENANCE log entry
    Returns the log_id for attaching files
    """
    # Verify equipment exists
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Update equipment maintenance fields
    equipment.last_maintenance_date = request.last_maintenance_date
    equipment.next_maintenance_date = request.next_maintenance_date
    equipment.maintenance_notes = request.maintenance_notes

    # Format dates for display in log
    last_date_str = request.last_maintenance_date.isoformat() if request.last_maintenance_date else 'N/A'
    next_date_str = request.next_maintenance_date.isoformat() if request.next_maintenance_date else 'N/A'

    # Create MAINTENANCE log entry with JSON format
    log = EquipmentLog(
        equipment_id=equipment.id,
        log_type=EquipmentLogType.MAINTENANCE,
        description=f"Maintenance Record: {request.maintenance_notes}",
        new_value=json.dumps({
            "last_maintenance_date": last_date_str,
            "next_maintenance_date": next_date_str
        }, ensure_ascii=False),
        created_by=current_user.id,
    )
    db.add(log)
    await db.flush()  # Flush to get the log ID

    await db.commit()
    await db.refresh(log)

    return {
        "message": "Maintenance record added successfully",
        "log_id": log.id
    }


# ==================== Parent-Child Equipment Management ====================

@router.get("/{equipment_id}/children", response_model=list[EquipmentResponse])
async def get_equipment_children(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all child equipment (sub-components) for a parent equipment
    """
    # Verify parent equipment exists
    parent_result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    parent_equipment = parent_result.scalar_one_or_none()

    if not parent_equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent equipment not found",
        )

    # Get all children with location and project info
    query = (
        select(Equipment)
        .where(
            Equipment.parent_equipment_id == equipment_id,
            Equipment.is_active == True
        )
        .options(selectinload(Equipment.current_location))
        .options(selectinload(Equipment.project))
        .order_by(Equipment.asset_code)
    )

    result = await db.execute(query)
    children = result.scalars().all()

    # Build response with location and project info
    children_response = []
    for child in children:
        child_dict = EquipmentResponse.model_validate(child).model_dump()

        # Add location info
        if child.current_location:
            child_dict['current_location_name'] = child.current_location.name
            child_dict['current_location_type'] = child.current_location.location_type.value

        # Add project info
        if child.project:
            child_dict['project_code'] = child.project.code
            child_dict['project_name'] = child.project.name

        children_response.append(EquipmentResponse(**child_dict))

    return children_response


@router.post("/{equipment_id}/detach-from-parent", response_model=EquipmentResponse)
async def detach_from_parent(
    equipment_id: int,
    request_data: DetachFromParentRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Detach equipment from its parent (Manager+ only)
    Makes the equipment independent
    """
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    if not equipment.parent_equipment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment is not attached to any parent",
        )

    # Get parent info for logging
    parent_result = await db.execute(
        select(Equipment).where(Equipment.id == equipment.parent_equipment_id)
    )
    parent_equipment = parent_result.scalar_one_or_none()
    parent_asset_code = parent_equipment.asset_code if parent_equipment else "Unknown"

    # Validate new location exists
    location_result = await db.execute(
        select(Location).where(Location.id == request_data.new_location_id)
    )
    new_location = location_result.scalar_one_or_none()
    if not new_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target location not found",
        )

    # Track old values for JSON logging
    old_parent_id = equipment.parent_equipment_id
    old_status = equipment.status
    old_location_id = equipment.current_location_id

    # Get old location info for JSON
    old_location_info = None
    if old_location_id:
        old_loc_result = await db.execute(
            select(Location).where(Location.id == old_location_id)
        )
        old_location = old_loc_result.scalar_one_or_none()
        if old_location:
            old_location_info = {
                "id": old_location.id,
                "name": old_location.name,
                "type": old_location.location_type.value if old_location.location_type else None
            }

    # Detach from parent
    equipment.parent_equipment_id = None

    # Update status
    if equipment.status.value != request_data.new_status.value:
        equipment.status = request_data.new_status

    # Update location
    if equipment.current_location_id != request_data.new_location_id:
        equipment.current_location_id = request_data.new_location_id

    # Log the detachment with JSON format
    description = f"Detached from parent equipment {parent_asset_code}"
    if request_data.notes:
        description += f" - {request_data.notes}"

    old_value_json = json.dumps({
        "parent_equipment_id": old_parent_id,
        "parent_asset_code": parent_asset_code,
        "status": old_status.value,
        "location": old_location_info
    }, ensure_ascii=False)

    new_value_json = json.dumps({
        "parent_equipment_id": None,
        "status": request_data.new_status.value,
        "location": {
            "id": new_location.id,
            "name": new_location.name,
            "type": new_location.location_type.value if new_location.location_type else None
        }
    }, ensure_ascii=False)

    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.UPDATED,
        description=description,
        old_value=old_value_json,
        new_value=new_value_json,
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.post("/{equipment_id}/group-move", response_model=dict)
async def group_move_equipment(
    equipment_id: int,
    request_data: GroupMoveRequest,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Move equipment and optionally all its children to a new location (group move).
    Also updates status to DEPLOYED when moving to vessel/person.
    """
    from app.models.location import Location

    # Verify equipment exists
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Verify target location exists
    loc_result = await db.execute(
        select(Location).where(Location.id == request_data.location_id)
    )
    target_location = loc_result.scalar_one_or_none()

    if not target_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target location not found",
        )

    moved_count = 0
    old_location_id = equipment.current_location_id
    old_status = equipment.status

    # Determine new status based on target location type
    # vessel/person -> DEPLOYED, warehouse -> IN_STOCK
    if target_location.location_type.value in ['vessel', 'person']:
        new_status = EquipmentStatus.DEPLOYED
    else:
        new_status = EquipmentStatus.IN_STOCK

    # Get old location info for JSON
    old_location_info = None
    if old_location_id:
        old_loc_result = await db.execute(
            select(Location).where(Location.id == old_location_id)
        )
        old_location = old_loc_result.scalar_one_or_none()
        if old_location:
            old_location_info = {
                "id": old_location.id,
                "name": old_location.name,
                "type": old_location.location_type.value if old_location.location_type else None
            }

    # Move parent equipment and update status
    equipment.current_location_id = request_data.location_id
    equipment.status = new_status

    # JSON format for log
    old_value_json = json.dumps({
        "status": old_status.value,
        "location": old_location_info
    }, ensure_ascii=False)

    new_value_json = json.dumps({
        "status": new_status.value,
        "location": {
            "id": target_location.id,
            "name": target_location.name,
            "type": target_location.location_type.value if target_location.location_type else None
        }
    }, ensure_ascii=False)

    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=request_data.notes or f"Moved to {target_location.name} (group move)",
        old_value=old_value_json,
        new_value=new_value_json,
        user_id=current_user.id,
    )
    moved_count += 1

    # Move children if requested
    if request_data.include_children:
        children_result = await db.execute(
            select(Equipment).where(
                Equipment.parent_equipment_id == equipment_id,
                Equipment.is_active == True
            )
        )
        children = children_result.scalars().all()

        for child in children:
            old_child_location_id = child.current_location_id
            old_child_status = child.status

            # Get old child location info
            old_child_location_info = None
            if old_child_location_id:
                old_child_loc_result = await db.execute(
                    select(Location).where(Location.id == old_child_location_id)
                )
                old_child_loc = old_child_loc_result.scalar_one_or_none()
                if old_child_loc:
                    old_child_location_info = {
                        "id": old_child_loc.id,
                        "name": old_child_loc.name,
                        "type": old_child_loc.location_type.value if old_child_loc.location_type else None
                    }

            # Update child location and status
            child.current_location_id = request_data.location_id
            child.status = new_status

            child_old_value_json = json.dumps({
                "status": old_child_status.value,
                "location": old_child_location_info
            }, ensure_ascii=False)

            await log_equipment_change(
                db=db,
                equipment_id=child.id,
                log_type=EquipmentLogType.STATUS_CHANGE,
                description=f"Moved with parent {equipment.asset_code} to {target_location.name}",
                old_value=child_old_value_json,
                new_value=new_value_json,
                user_id=current_user.id,
            )
            moved_count += 1

    await db.commit()

    return {
        "message": "Equipment moved successfully",
        "moved_count": moved_count,
        "target_location": target_location.name,
        "new_status": new_status.value
    }


@router.post("/{equipment_id}/sync-children-status", response_model=dict)
async def sync_children_status(
    equipment_id: int,
    request_data: SyncChildrenStatusRequest,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Change equipment status and optionally sync all children to the same status
    """
    # Verify equipment exists
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    updated_count = 0
    old_status = equipment.status

    # Update parent equipment status
    equipment.status = request_data.new_status

    # JSON format for log
    old_value_json = json.dumps({"status": old_status.value}, ensure_ascii=False)
    new_value_json = json.dumps({"status": request_data.new_status.value}, ensure_ascii=False)

    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=request_data.notes or f"Status changed to {request_data.new_status.value}",
        old_value=old_value_json,
        new_value=new_value_json,
        user_id=current_user.id,
    )
    updated_count += 1

    # Sync children if requested
    if request_data.include_children:
        children_result = await db.execute(
            select(Equipment).where(
                Equipment.parent_equipment_id == equipment_id,
                Equipment.is_active == True
            )
        )
        children = children_result.scalars().all()

        for child in children:
            old_child_status = child.status
            child.status = request_data.new_status

            child_old_value_json = json.dumps({"status": old_child_status.value}, ensure_ascii=False)

            await log_equipment_change(
                db=db,
                equipment_id=child.id,
                log_type=EquipmentLogType.STATUS_CHANGE,
                description=f"Status synced with parent {equipment.asset_code} to {request_data.new_status.value}",
                old_value=child_old_value_json,
                new_value=new_value_json,
                user_id=current_user.id,
            )
            updated_count += 1

    await db.commit()

    return {
        "message": "Status updated successfully",
        "updated_count": updated_count,
        "new_status": request_data.new_status.value
    }
