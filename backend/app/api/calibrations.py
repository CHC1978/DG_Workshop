"""Calibration management API endpoints"""
from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager
from app.models.user import User
from app.models.calibration import Calibration
from app.models.equipment import Equipment
from app.models.equipment_log import EquipmentLogType
from app.schemas.calibration import (
    CalibrationCreate,
    CalibrationUpdate,
    CalibrationResponse,
    CalibrationListResponse,
    CalibrationDetailResponse,
    CalibrationDueSoonResponse,
)
from app.schemas.equipment import EquipmentResponse
from app.api.equipment import log_equipment_change

router = APIRouter(prefix="/calibrations", tags=["Calibrations"])


# ==================== CRUD Operations ====================

@router.get("", response_model=CalibrationListResponse)
async def list_calibrations(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all calibration records with filtering and pagination
    """
    query = select(Calibration)

    # Apply filters
    if equipment_id:
        query = query.where(Calibration.equipment_id == equipment_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Calibration.next_due_date.desc())
    result = await db.execute(query)
    calibrations = result.scalars().all()

    return CalibrationListResponse(
        calibrations=[CalibrationResponse.model_validate(c) for c in calibrations],
        total=total
    )


@router.post("", response_model=CalibrationResponse, status_code=status.HTTP_201_CREATED)
async def create_calibration(
    calibration_data: CalibrationCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new calibration record (Manager+ only)
    """
    # Verify equipment exists
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == calibration_data.equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Validate dates
    if calibration_data.next_due_date < calibration_data.calibration_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Next due date must be after calibration date",
        )

    # Create calibration record
    new_calibration = Calibration(
        equipment_id=calibration_data.equipment_id,
        calibration_date=calibration_data.calibration_date,
        next_due_date=calibration_data.next_due_date,
        provider=calibration_data.provider,
        certificate_number=calibration_data.certificate_number,
        cost=calibration_data.cost,
        notes=calibration_data.notes,
    )

    db.add(new_calibration)
    await db.flush()

    # Log calibration in equipment log
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.CALIBRATION,
        description=f"Calibration by {calibration_data.provider}. Next due: {calibration_data.next_due_date}",
        new_value=f"Certificate: {calibration_data.certificate_number or 'N/A'}",
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(new_calibration)

    return CalibrationResponse.model_validate(new_calibration)


@router.get("/due-soon", response_model=list[CalibrationDueSoonResponse])
async def get_calibrations_due_soon(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get calibrations due soon (within specified days)
    Default: 30 days
    """
    print(f"[DEBUG] days parameter: {days}, type: {type(days)}")
    today = date.today()
    future_date = today + timedelta(days=days)

    # Find calibrations due within the period
    query = (
        select(Calibration)
        .where(Calibration.next_due_date <= future_date)
        .order_by(Calibration.next_due_date)
    )

    result = await db.execute(query)
    calibrations = result.scalars().all()

    # Build response with equipment info
    responses = []
    for cal in calibrations:
        # Get equipment
        equipment_result = await db.execute(
            select(Equipment).where(Equipment.id == cal.equipment_id)
        )
        equipment = equipment_result.scalar_one_or_none()

        if equipment:
            days_until_due = (cal.next_due_date - today).days
            is_overdue = days_until_due < 0

            responses.append(
                CalibrationDueSoonResponse(
                    calibration=CalibrationResponse.model_validate(cal),
                    equipment_asset_code=equipment.asset_code,
                    equipment_name=f"{equipment.manufacturer} {equipment.model}",
                    days_until_due=days_until_due,
                    is_overdue=is_overdue,
                )
            )

    return responses

@router.get("/{calibration_id}", response_model=CalibrationDetailResponse)
async def get_calibration(
    calibration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get calibration by ID with equipment info
    """
    result = await db.execute(
        select(Calibration).where(Calibration.id == calibration_id)
    )
    calibration = result.scalar_one_or_none()

    if not calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibration not found",
        )

    # Get related equipment
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == calibration.equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    # Build response
    response = CalibrationDetailResponse.model_validate(calibration)
    if equipment:
        response.equipment = EquipmentResponse.model_validate(equipment).model_dump()

    return response


@router.put("/{calibration_id}", response_model=CalibrationResponse)
async def update_calibration(
    calibration_id: int,
    calibration_data: CalibrationUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update calibration record (Manager+ only)
    """
    result = await db.execute(
        select(Calibration).where(Calibration.id == calibration_id)
    )
    calibration = result.scalar_one_or_none()

    if not calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibration not found",
        )

    # Update fields
    update_data = calibration_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(calibration, field):
            setattr(calibration, field, value)

    await db.commit()
    await db.refresh(calibration)

    return CalibrationResponse.model_validate(calibration)


@router.delete("/{calibration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calibration(
    calibration_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete calibration record permanently (Admin only)
    """
    result = await db.execute(
        select(Calibration).where(Calibration.id == calibration_id)
    )
    calibration = result.scalar_one_or_none()

    if not calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibration not found",
        )

    await db.delete(calibration)
    await db.commit()


# ==================== Calibration Due Date Checking ====================


@router.get("/equipment/{equipment_id}", response_model=list[CalibrationResponse])
async def get_equipment_calibrations(
    equipment_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all calibration records for a specific equipment
    """
    # Verify equipment exists
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Get calibrations
    query = (
        select(Calibration)
        .where(Calibration.equipment_id == equipment_id)
        .order_by(Calibration.calibration_date.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    calibrations = result.scalars().all()

    return [CalibrationResponse.model_validate(c) for c in calibrations]
