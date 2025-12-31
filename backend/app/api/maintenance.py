"""Maintenance management API endpoints"""
from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager, require_admin
from app.models.user import User
from app.models.maintenance import Maintenance
from app.models.equipment import Equipment
from app.models.equipment_log import EquipmentLogType
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceResponse,
    MaintenanceListResponse,
    MaintenanceDetailResponse,
    MaintenanceDueSoonResponse,
)
from app.schemas.equipment import EquipmentResponse
from app.api.equipment import log_equipment_change

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


# ==================== CRUD Operations ====================

@router.get("", response_model=MaintenanceListResponse)
async def list_maintenance(
    skip: int = 0,
    limit: int = 100,
    equipment_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all maintenance records with filtering and pagination
    """
    query = select(Maintenance)

    # Apply filters
    if equipment_id:
        query = query.where(Maintenance.equipment_id == equipment_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Maintenance.next_due_date.desc())
    result = await db.execute(query)
    maintenances = result.scalars().all()

    return MaintenanceListResponse(
        maintenances=[MaintenanceResponse.model_validate(m) for m in maintenances],
        total=total
    )


@router.post("", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    maintenance_data: MaintenanceCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new maintenance record (Manager+ only)
    """
    # Verify equipment exists
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == maintenance_data.equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Validate dates
    if maintenance_data.next_due_date < maintenance_data.maintenance_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Next due date must be after maintenance date",
        )

    # Create maintenance record
    new_maintenance = Maintenance(
        equipment_id=maintenance_data.equipment_id,
        maintenance_date=maintenance_data.maintenance_date,
        next_due_date=maintenance_data.next_due_date,
        provider=maintenance_data.provider,
        service_type=maintenance_data.service_type,
        cost=maintenance_data.cost,
        notes=maintenance_data.notes,
    )

    db.add(new_maintenance)
    await db.flush()

    # Update Equipment.next_maintenance_date to the latest
    equipment.next_maintenance_date = maintenance_data.next_due_date
    equipment.last_maintenance_date = maintenance_data.maintenance_date

    # Log maintenance in equipment log
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.MAINTENANCE,
        description=f"Maintenance by {maintenance_data.provider}. Next due: {maintenance_data.next_due_date}",
        new_value=f"Service Type: {maintenance_data.service_type or 'N/A'}",
        user_id=current_user.id,
    )

    await db.commit()
    await db.refresh(new_maintenance)

    return MaintenanceResponse.model_validate(new_maintenance)


@router.get("/due-soon", response_model=list[MaintenanceDueSoonResponse])
async def get_maintenance_due_soon(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get maintenance due soon (within specified days)
    Default: 30 days
    """
    today = date.today()
    future_date = today + timedelta(days=days)

    # Find maintenance due within the period
    query = (
        select(Maintenance)
        .where(Maintenance.next_due_date <= future_date)
        .order_by(Maintenance.next_due_date)
    )

    result = await db.execute(query)
    maintenances = result.scalars().all()

    # Build response with equipment info
    responses = []
    for maint in maintenances:
        # Get equipment
        equipment_result = await db.execute(
            select(Equipment).where(Equipment.id == maint.equipment_id)
        )
        equipment = equipment_result.scalar_one_or_none()

        if equipment:
            days_until_due = (maint.next_due_date - today).days
            is_overdue = days_until_due < 0

            responses.append(
                MaintenanceDueSoonResponse(
                    maintenance=MaintenanceResponse.model_validate(maint),
                    equipment_asset_code=equipment.asset_code,
                    equipment_name=f"{equipment.manufacturer} {equipment.model}",
                    days_until_due=days_until_due,
                    is_overdue=is_overdue,
                )
            )

    return responses


@router.get("/{maintenance_id}", response_model=MaintenanceDetailResponse)
async def get_maintenance(
    maintenance_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get maintenance by ID with equipment info
    """
    result = await db.execute(
        select(Maintenance).where(Maintenance.id == maintenance_id)
    )
    maintenance = result.scalar_one_or_none()

    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found",
        )

    # Get related equipment
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == maintenance.equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    # Build response
    response = MaintenanceDetailResponse.model_validate(maintenance)
    if equipment:
        response.equipment = EquipmentResponse.model_validate(equipment).model_dump()

    return response


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance(
    maintenance_id: int,
    maintenance_data: MaintenanceUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update maintenance record (Manager+ only)
    """
    result = await db.execute(
        select(Maintenance).where(Maintenance.id == maintenance_id)
    )
    maintenance = result.scalar_one_or_none()

    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found",
        )

    # Update fields
    update_data = maintenance_data.model_dump(exclude_unset=True)

    # If next_due_date is updated, also update Equipment.next_maintenance_date
    if "next_due_date" in update_data:
        equipment_result = await db.execute(
            select(Equipment).where(Equipment.id == maintenance.equipment_id)
        )
        equipment = equipment_result.scalar_one_or_none()
        if equipment:
            equipment.next_maintenance_date = update_data["next_due_date"]

    # If maintenance_date is updated, also update Equipment.last_maintenance_date
    if "maintenance_date" in update_data:
        equipment_result = await db.execute(
            select(Equipment).where(Equipment.id == maintenance.equipment_id)
        )
        equipment = equipment_result.scalar_one_or_none()
        if equipment:
            equipment.last_maintenance_date = update_data["maintenance_date"]

    for field, value in update_data.items():
        if hasattr(maintenance, field):
            setattr(maintenance, field, value)

    await db.commit()
    await db.refresh(maintenance)

    return MaintenanceResponse.model_validate(maintenance)


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance(
    maintenance_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete maintenance record permanently (Admin only)
    """
    result = await db.execute(
        select(Maintenance).where(Maintenance.id == maintenance_id)
    )
    maintenance = result.scalar_one_or_none()

    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found",
        )

    await db.delete(maintenance)
    await db.commit()


@router.get("/equipment/{equipment_id}", response_model=list[MaintenanceResponse])
async def get_equipment_maintenance(
    equipment_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all maintenance records for a specific equipment
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

    # Get maintenance records
    query = (
        select(Maintenance)
        .where(Maintenance.equipment_id == equipment_id)
        .order_by(Maintenance.maintenance_date.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    maintenances = result.scalars().all()

    return [MaintenanceResponse.model_validate(m) for m in maintenances]
