"""SubEquipment management API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager
from app.models.user import User
from app.models.equipment import Equipment, EquipmentStatus
from app.models.sub_equipment import SubEquipment
from app.models.equipment_log import EquipmentLog, EquipmentLogType
from app.schemas.sub_equipment import (
    SubEquipmentCreate,
    SubEquipmentUpdate,
    SubEquipmentResponse,
    SubEquipmentListResponse,
    SubEquipmentDetailResponse,
)
from app.schemas.equipment import EquipmentLogResponse
from app.utils.asset_code import generate_sub_equipment_asset_code, generate_qr_code_url

router = APIRouter(prefix="/sub-equipment", tags=["SubEquipment"])


async def log_sub_equipment_change(
    db: AsyncSession,
    sub_equipment_id: int,
    log_type: EquipmentLogType,
    description: str,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    user_id: Optional[int] = None,
):
    """Helper function to log sub-equipment changes"""
    log = EquipmentLog(
        equipment_id=sub_equipment_id,
        is_sub_equipment=True,  # 標記為子設備
        log_type=log_type,
        old_value=old_value,
        new_value=new_value,
        description=description,
        created_by=user_id,
    )
    db.add(log)


# ==================== CRUD Operations ====================

@router.get("", response_model=SubEquipmentListResponse)
async def list_sub_equipment(
    parent_equipment_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all sub-equipment with filtering

    - **parent_equipment_id**: Filter by parent equipment (optional)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    query = select(SubEquipment).where(SubEquipment.is_active == True)

    if parent_equipment_id:
        query = query.where(SubEquipment.parent_equipment_id == parent_equipment_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(SubEquipment.created_at.desc())
    result = await db.execute(query)
    sub_equipment_list = result.scalars().all()

    return SubEquipmentListResponse(
        sub_equipments=[SubEquipmentResponse.model_validate(se) for se in sub_equipment_list],
        total=total
    )


@router.post("", response_model=SubEquipmentResponse, status_code=http_status.HTTP_201_CREATED)
async def create_sub_equipment(
    sub_equipment_data: SubEquipmentCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new sub-equipment (Manager+ only)

    Auto-generates asset code and QR code based on parent equipment.

    - **parent_equipment_id**: ID of the parent equipment
    - **component_name**: Name of the component (e.g., "天線1", "IMU Cable")
    - **serial_number**: Serial number (optional)
    - **notes**: Additional notes (optional)
    """
    # Verify parent equipment exists
    result = await db.execute(
        select(Equipment).where(Equipment.id == sub_equipment_data.parent_equipment_id)
    )
    parent_equipment = result.scalar_one_or_none()

    if not parent_equipment:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Parent equipment not found"
        )

    # Generate asset code
    asset_code = await generate_sub_equipment_asset_code(parent_equipment.asset_code, db)

    # Generate QR code URL
    qr_code = generate_qr_code_url(asset_code)

    # Create sub-equipment
    new_sub_equipment = SubEquipment(
        parent_equipment_id=sub_equipment_data.parent_equipment_id,
        asset_code=asset_code,
        qr_code=qr_code,
        component_name=sub_equipment_data.component_name,
        serial_number=sub_equipment_data.serial_number,
        notes=sub_equipment_data.notes,
        status=EquipmentStatus.IN_STOCK,
        is_active=True,
    )

    db.add(new_sub_equipment)
    await db.flush()

    # Log creation
    await log_sub_equipment_change(
        db=db,
        sub_equipment_id=new_sub_equipment.id,
        log_type=EquipmentLogType.CREATED,
        description=f"Sub-equipment created: {asset_code} ({sub_equipment_data.component_name})",
        new_value=f"Status: {EquipmentStatus.IN_STOCK.value}",
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(new_sub_equipment)

    return SubEquipmentResponse.model_validate(new_sub_equipment)


@router.get("/{sub_equipment_id}", response_model=SubEquipmentDetailResponse)
async def get_sub_equipment(
    sub_equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sub-equipment by ID with parent info

    Returns detailed information including parent equipment details.
    """
    result = await db.execute(
        select(SubEquipment, Equipment)
        .join(Equipment, SubEquipment.parent_equipment_id == Equipment.id)
        .where(SubEquipment.id == sub_equipment_id)
    )
    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Sub-equipment not found"
        )

    sub_equipment, parent = row

    # Build response with parent info
    response_dict = SubEquipmentDetailResponse.model_validate(sub_equipment).model_dump()
    response_dict['parent_asset_code'] = parent.asset_code
    response_dict['parent_model'] = f"{parent.manufacturer} {parent.model}"

    return SubEquipmentDetailResponse(**response_dict)


@router.put("/{sub_equipment_id}", response_model=SubEquipmentResponse)
async def update_sub_equipment(
    sub_equipment_id: int,
    sub_equipment_data: SubEquipmentUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update sub-equipment (Manager+ only)

    Can update component_name, serial_number, status, and notes.
    Changes are logged in the equipment log.
    """
    result = await db.execute(
        select(SubEquipment).where(SubEquipment.id == sub_equipment_id)
    )
    sub_equipment = result.scalar_one_or_none()

    if not sub_equipment:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Sub-equipment not found"
        )

    # Track changes
    changes = []
    update_data = sub_equipment_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(sub_equipment, field):
            old_value = getattr(sub_equipment, field)
            if old_value != value:
                # Convert enum to value for logging
                old_val_str = old_value.value if hasattr(old_value, 'value') else str(old_value)
                new_val_str = value.value if hasattr(value, 'value') else str(value)
                changes.append(f"{field}: {old_val_str} -> {new_val_str}")
                setattr(sub_equipment, field, value)

    # Log changes
    if changes:
        await log_sub_equipment_change(
            db=db,
            sub_equipment_id=sub_equipment.id,
            log_type=EquipmentLogType.UPDATED,
            description=f"Sub-equipment updated",
            old_value="; ".join(changes[:5]),  # Limit to first 5 changes
            user_id=current_user.id,
        )

    await db.commit()
    await db.refresh(sub_equipment)

    return SubEquipmentResponse.model_validate(sub_equipment)


@router.delete("/{sub_equipment_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_sub_equipment(
    sub_equipment_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (deactivate) sub-equipment (Manager+ only)

    Performs soft delete by setting is_active=False.
    """
    result = await db.execute(
        select(SubEquipment).where(SubEquipment.id == sub_equipment_id)
    )
    sub_equipment = result.scalar_one_or_none()

    if not sub_equipment:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Sub-equipment not found"
        )

    # Soft delete
    sub_equipment.is_active = False

    # Log deletion
    await log_sub_equipment_change(
        db=db,
        sub_equipment_id=sub_equipment.id,
        log_type=EquipmentLogType.STATUS_CHANGE,
        description=f"Sub-equipment deactivated",
        old_value="is_active: True",
        new_value="is_active: False",
        user_id=current_user.id,
    )

    await db.commit()


@router.get("/{sub_equipment_id}/logs", response_model=list[EquipmentLogResponse])
async def get_sub_equipment_logs(
    sub_equipment_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sub-equipment change logs

    Returns activity history for this sub-equipment.
    """
    # Verify sub-equipment exists
    result = await db.execute(
        select(SubEquipment).where(SubEquipment.id == sub_equipment_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Sub-equipment not found"
        )

    # Get logs (注意：is_sub_equipment=True)
    query = (
        select(EquipmentLog, User)
        .outerjoin(User, EquipmentLog.created_by == User.id)
        .where(
            EquipmentLog.equipment_id == sub_equipment_id,
            EquipmentLog.is_sub_equipment == True
        )
        .order_by(EquipmentLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    log_user_pairs = result.all()

    # Build response with username
    responses = []
    for log, user in log_user_pairs:
        log_dict = EquipmentLogResponse.model_validate(log).model_dump()
        log_dict['created_by_username'] = user.username if user else None
        responses.append(EquipmentLogResponse(**log_dict))

    return responses
