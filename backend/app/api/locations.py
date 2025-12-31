"""Location management API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager, require_admin
from app.models.user import User
from app.models.location import Location, LocationType
from app.models.equipment import Equipment
from app.models.project import Project
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationListResponse,
    LocationDetailResponse,
)
from app.schemas.equipment import EquipmentResponse

router = APIRouter(prefix="/locations", tags=["Locations"])


# ==================== CRUD Operations ====================

@router.get("", response_model=LocationListResponse)
async def list_locations(
    skip: int = 0,
    limit: int = 100,
    location_type: Optional[LocationType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all locations with filtering and pagination
    """
    query = select(Location).where(Location.is_active == True)

    # Apply filters
    if location_type:
        query = query.where(Location.location_type == location_type)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Location.name)
    result = await db.execute(query)
    locations = result.scalars().all()

    return LocationListResponse(
        locations=[LocationResponse.model_validate(loc) for loc in locations],
        total=total
    )


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new location (Manager+ only)
    """
    # Check if code already exists (if provided)
    if location_data.code:
        result = await db.execute(
            select(Location).where(Location.code == location_data.code)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location code already exists",
            )

    # Create location using all fields from schema
    location_dict = location_data.model_dump()
    new_location = Location(**location_dict, is_active=True)

    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)

    return LocationResponse.model_validate(new_location)


@router.get("/{location_id}", response_model=LocationDetailResponse)
async def get_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get location by ID with equipment count and project info
    """
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    # Get equipment count at this location
    count_result = await db.execute(
        select(func.count(Equipment.id))
        .where(Equipment.current_location_id == location_id)
        .where(Equipment.is_active == True)
    )
    equipment_count = count_result.scalar()

    # Get project info if associated
    project_name = None
    project_code = None
    if location.current_project_id:
        project_result = await db.execute(
            select(Project).where(Project.id == location.current_project_id)
        )
        project = project_result.scalar_one_or_none()
        if project:
            project_name = project.name
            project_code = project.code

    # Build response
    response_dict = LocationDetailResponse.model_validate(location).model_dump()
    response_dict['equipment_count'] = equipment_count
    response_dict['project_name'] = project_name
    response_dict['project_code'] = project_code

    return LocationDetailResponse(**response_dict)


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    location_data: LocationUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update location (Manager+ only)
    """
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    # Check if new code already exists
    if location_data.code and location_data.code != location.code:
        result = await db.execute(
            select(Location).where(
                Location.code == location_data.code,
                Location.id != location_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location code already exists",
            )

    # Update fields
    update_data = location_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(location, field):
            setattr(location, field, value)

    await db.commit()
    await db.refresh(location)

    return LocationResponse.model_validate(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (deactivate) location (Admin only)
    Uses soft delete by setting is_active to False
    """
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    # Check if there are active equipment at this location
    count_result = await db.execute(
        select(func.count(Equipment.id))
        .where(Equipment.current_location_id == location_id)
        .where(Equipment.is_active == True)
    )
    equipment_count = count_result.scalar()

    if equipment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete location with {equipment_count} active equipment. Move equipment first.",
        )

    # Soft delete
    location.is_active = False
    await db.commit()


# ==================== Location Equipment ====================

@router.get("/{location_id}/equipment", response_model=list[EquipmentResponse])
async def get_location_equipment(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all equipment at a location
    """
    # Verify location exists
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    # Get equipment at this location
    result = await db.execute(
        select(Equipment)
        .where(Equipment.current_location_id == location_id)
        .where(Equipment.is_active == True)
        .order_by(Equipment.asset_code)
    )
    equipment_list = result.scalars().all()

    return [EquipmentResponse.model_validate(eq) for eq in equipment_list]
