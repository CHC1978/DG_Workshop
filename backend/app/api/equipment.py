"""Equipment management API endpoints"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager, require_admin, require_operator
from app.models.user import User
from app.models.equipment import Equipment, EquipmentStatus, EquipmentCategory
from app.models.equipment_log import EquipmentLog, EquipmentLogType
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
    EquipmentDetailResponse,
    EquipmentLogResponse,
    EquipmentLogUpdateRequest,
)
from app.utils.asset_code import generate_asset_code, generate_asset_code_v2, generate_qr_code_url, clean_model_code

router = APIRouter(prefix="/equipment", tags=["Equipment"])


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
    """Helper function to log equipment changes"""
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
    db.add(log)


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
    """
    from sqlalchemy.orm import selectinload
    from app.models.location import Location
    from app.models.project import Project

    query = select(Equipment).where(Equipment.is_active == True)

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
        .offset(skip)
        .limit(limit)
        .order_by(Equipment.created_at.desc())
    )
    result = await db.execute(query)
    equipment_list = result.scalars().all()

    # Build response with location and project info
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

    # Log creation
    await log_equipment_change(
        db=db,
        equipment_id=new_equipment.id,
        log_type=EquipmentLogType.CREATED,
        description=f"Equipment created: {asset_code}",
        new_value=f"Status: {EquipmentStatus.ORDERING.value}",
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
    Get equipment by ID
    """
    from sqlalchemy.orm import selectinload
    from app.models.location import Location

    result = await db.execute(
        select(Equipment)
        .options(selectinload(Equipment.current_location))
        .where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    return EquipmentDetailResponse.model_validate(equipment)


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
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Track changes for logging
    changes = []

    # Update fields
    update_data = equipment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(equipment, field):
            old_value = getattr(equipment, field)
            if old_value != value:
                changes.append(f"{field}: {old_value} -> {value}")
                setattr(equipment, field, value)

    # Log changes
    if changes:
        await log_equipment_change(
            db=db,
            equipment_id=equipment.id,
            log_type=EquipmentLogType.UPDATED,
            description=f"Equipment updated",
            old_value="; ".join(changes[:5]),  # Limit to first 5 changes
            user_id=current_user.id,
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

    # Log deletion
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=f"Equipment deactivated",
        old_value="is_active: True",
        new_value="is_active: False",
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

    # Build response with usernames and current location/project
    responses = []
    for log, creator, editor in log_rows:
        log_dict = EquipmentLogResponse.model_validate(log).model_dump()
        log_dict['created_by_username'] = creator.username if creator else None
        log_dict['edited_by_username'] = editor.username if editor else None
        log_dict['is_edited'] = log.edit_count > 0

        # Add current equipment location and project info
        if current_location:
            log_dict['current_location_name'] = current_location.name
            log_dict['current_location_type'] = current_location.location_type.value
        if current_project:
            log_dict['project_code'] = current_project.code
            log_dict['project_name'] = current_project.name

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


# ==================== Status Change Operations ====================

@router.post("/{equipment_id}/deploy", response_model=EquipmentResponse)
async def deploy_equipment(
    equipment_id: int,
    location_id: int,
    notes: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
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
    if equipment.status not in [EquipmentStatus.IN_STOCK, EquipmentStatus.ORDERING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deploy equipment with status: {equipment.status.value}",
        )

    # Update status and location
    old_status = equipment.status
    old_location = equipment.current_location_id

    equipment.status = EquipmentStatus.DEPLOYED
    equipment.current_location_id = location_id

    # Log the deployment
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=notes or f"Equipment deployed to location {location_id}",
        old_value=f"Status: {old_status.value}, Location: {old_location}",
        new_value=f"Status: {EquipmentStatus.DEPLOYED.value}, Location: {location_id}",
        user_id=current_user.id,
        latitude=latitude,
        longitude=longitude,
    )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.post("/{equipment_id}/return", response_model=EquipmentResponse)
async def return_equipment(
    equipment_id: int,
    location_id: int,
    notes: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
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

    # Update status and location
    old_status = equipment.status
    old_location = equipment.current_location_id

    equipment.status = EquipmentStatus.IN_STOCK
    equipment.current_location_id = location_id

    # Log the return
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=notes or f"Equipment returned to location {location_id}",
        old_value=f"Status: {old_status.value}, Location: {old_location}",
        new_value=f"Status: {EquipmentStatus.IN_STOCK.value}, Location: {location_id}",
        user_id=current_user.id,
        latitude=latitude,
        longitude=longitude,
    )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.post("/{equipment_id}/repair", response_model=EquipmentResponse)
async def send_to_repair(
    equipment_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Send equipment to repair (Operator+ only)
    Changes status to REPAIR
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

    # Update status
    old_status = equipment.status
    equipment.status = EquipmentStatus.REPAIR

    # Log the repair
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.MAINTENANCE,
        description=notes or "Equipment sent to repair",
        old_value=f"Status: {old_status.value}",
        new_value=f"Status: {EquipmentStatus.REPAIR.value}",
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(equipment)

    return EquipmentResponse.model_validate(equipment)


@router.post("/{equipment_id}/send-to-calibration", response_model=EquipmentResponse)
async def send_to_calibration(
    equipment_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(require_operator),
    db: AsyncSession = Depends(get_db)
):
    """
    Send equipment to calibration (Operator+ only)
    Changes status to CALIBRATING
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

    # Update status
    old_status = equipment.status
    equipment.status = EquipmentStatus.CALIBRATING

    # Log the calibration send
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.CALIBRATION,
        description=notes or "Equipment sent to calibration",
        old_value=f"Status: {old_status.value}",
        new_value=f"Status: {EquipmentStatus.CALIBRATING.value}",
        user_id=current_user.id,
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
