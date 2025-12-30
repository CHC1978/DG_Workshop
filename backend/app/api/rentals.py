"""Rental management API endpoints"""
from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager
from app.models.user import User
from app.models.rental import Rental, RentalStatus
from app.models.equipment import Equipment, EquipmentStatus
from app.models.customer import Customer
from app.models.equipment_log import EquipmentLogType
from app.schemas.rental import (
    RentalCreate,
    RentalUpdate,
    RentalResponse,
    RentalListResponse,
    RentalDetailResponse,
    RentalConfirmRequest,
    RentalDeliverRequest,
    RentalReturnRequest,
    RentalCancelRequest,
)
from app.schemas.equipment import EquipmentResponse
from app.schemas.customer import CustomerResponse
from app.utils.rental_number import generate_rental_number
from app.api.equipment import log_equipment_change

router = APIRouter(prefix="/rentals", tags=["Rentals"])


def calculate_rental_amount(daily_rate: float, start_date: date, end_date: date) -> float:
    """Calculate total rental amount"""
    days = (end_date - start_date).days + 1  # Include both start and end day
    return daily_rate * days


# ==================== CRUD Operations ====================

@router.get("", response_model=RentalListResponse)
async def list_rentals(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[RentalStatus] = None,
    customer_id: Optional[int] = None,
    equipment_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all rentals with filtering and pagination
    """
    query = select(Rental)

    # Apply filters
    if status_filter:
        query = query.where(Rental.status == status_filter)
    if customer_id:
        query = query.where(Rental.customer_id == customer_id)
    if equipment_id:
        query = query.where(Rental.equipment_id == equipment_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Rental.created_at.desc())
    result = await db.execute(query)
    rentals = result.scalars().all()

    return RentalListResponse(
        rentals=[RentalResponse.model_validate(r) for r in rentals],
        total=total
    )


@router.post("", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def create_rental(
    rental_data: RentalCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new rental (Manager+ only)
    Initial status is DRAFT
    """
    # Verify equipment exists and is available
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == rental_data.equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    if equipment.status not in [EquipmentStatus.IN_STOCK, EquipmentStatus.ORDERING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Equipment is not available for rental (status: {equipment.status.value})",
        )

    # Verify customer exists
    customer_result = await db.execute(
        select(Customer).where(Customer.id == rental_data.customer_id)
    )
    customer = customer_result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer is not active",
        )

    # Validate dates
    if rental_data.expected_end_date < rental_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Generate rental number
    rental_number = await generate_rental_number(db)

    # Create rental
    new_rental = Rental(
        rental_number=rental_number,
        equipment_id=rental_data.equipment_id,
        customer_id=rental_data.customer_id,
        start_date=rental_data.start_date,
        expected_end_date=rental_data.expected_end_date,
        daily_rate=rental_data.daily_rate,
        deposit_amount=rental_data.deposit_amount,
        notes=rental_data.notes,
        status=RentalStatus.DRAFT,
    )

    db.add(new_rental)
    await db.commit()
    await db.refresh(new_rental)

    return RentalResponse.model_validate(new_rental)


@router.get("/{rental_id}", response_model=RentalDetailResponse)
async def get_rental(
    rental_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get rental by ID with related equipment and customer info
    """
    result = await db.execute(
        select(Rental).where(Rental.id == rental_id)
    )
    rental = result.scalar_one_or_none()

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found",
        )

    # Get related equipment
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == rental.equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    # Get related customer
    customer_result = await db.execute(
        select(Customer).where(Customer.id == rental.customer_id)
    )
    customer = customer_result.scalar_one_or_none()

    # Build response
    response = RentalDetailResponse.model_validate(rental)
    if equipment:
        response.equipment = EquipmentResponse.model_validate(equipment).model_dump()
    if customer:
        response.customer = CustomerResponse.model_validate(customer).model_dump()

    return response


@router.put("/{rental_id}", response_model=RentalResponse)
async def update_rental(
    rental_id: int,
    rental_data: RentalUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update rental (Manager+ only)
    Can only update rentals in DRAFT or CONFIRMED status
    """
    result = await db.execute(
        select(Rental).where(Rental.id == rental_id)
    )
    rental = result.scalar_one_or_none()

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found",
        )

    # Check if rental can be updated
    if rental.status not in [RentalStatus.DRAFT, RentalStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update rental with status: {rental.status.value}",
        )

    # Update fields
    update_data = rental_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(rental, field):
            setattr(rental, field, value)

    await db.commit()
    await db.refresh(rental)

    return RentalResponse.model_validate(rental)


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental(
    rental_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete rental (Manager+ only)
    Can only delete rentals in DRAFT status
    """
    result = await db.execute(
        select(Rental).where(Rental.id == rental_id)
    )
    rental = result.scalar_one_or_none()

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found",
        )

    # Can only delete draft rentals
    if rental.status != RentalStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete rentals in DRAFT status",
        )

    await db.delete(rental)
    await db.commit()


# ==================== Rental Status Operations ====================

@router.post("/{rental_id}/confirm", response_model=RentalResponse)
async def confirm_rental(
    rental_id: int,
    request: RentalConfirmRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm rental (Manager+ only)
    Changes status from DRAFT to CONFIRMED
    """
    result = await db.execute(
        select(Rental).where(Rental.id == rental_id)
    )
    rental = result.scalar_one_or_none()

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found",
        )

    if rental.status != RentalStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only confirm rentals in DRAFT status (current: {rental.status.value})",
        )

    # Update status
    rental.status = RentalStatus.CONFIRMED
    if request.notes:
        rental.notes = request.notes

    await db.commit()
    await db.refresh(rental)

    return RentalResponse.model_validate(rental)


@router.post("/{rental_id}/deliver", response_model=RentalResponse)
async def deliver_rental(
    rental_id: int,
    request: RentalDeliverRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Deliver rental equipment to customer (Manager+ only)
    Changes rental status to ACTIVE and equipment status to RENTED
    """
    result = await db.execute(
        select(Rental).where(Rental.id == rental_id)
    )
    rental = result.scalar_one_or_none()

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found",
        )

    if rental.status != RentalStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only deliver confirmed rentals (current: {rental.status.value})",
        )

    # Get equipment
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == rental.equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Update rental status
    rental.status = RentalStatus.ACTIVE
    if request.delivery_notes:
        rental.delivery_notes = request.delivery_notes

    # Calculate total amount
    rental.total_amount = calculate_rental_amount(
        rental.daily_rate,
        rental.start_date,
        rental.expected_end_date
    )

    # Update equipment status
    old_status = equipment.status
    equipment.status = EquipmentStatus.RENTED

    # Log equipment rental start
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.RENTAL_START,
        description=f"Rented to {rental.customer.company_name} (Rental: {rental.rental_number})",
        old_value=f"Status: {old_status.value}",
        new_value=f"Status: {EquipmentStatus.RENTED.value}",
        user_id=current_user.id,
        latitude=request.latitude,
        longitude=request.longitude,
    )

    await db.commit()
    await db.refresh(rental)

    return RentalResponse.model_validate(rental)


@router.post("/{rental_id}/return", response_model=RentalResponse)
async def return_rental(
    rental_id: int,
    request: RentalReturnRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Return rental equipment from customer (Manager+ only)
    Changes rental status to RETURNED and equipment status to IN_STOCK
    Recalculates total amount based on actual return date
    """
    result = await db.execute(
        select(Rental).where(Rental.id == rental_id)
    )
    rental = result.scalar_one_or_none()

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found",
        )

    if rental.status not in [RentalStatus.ACTIVE, RentalStatus.OVERDUE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only return active or overdue rentals (current: {rental.status.value})",
        )

    # Get equipment
    equipment_result = await db.execute(
        select(Equipment).where(Equipment.id == rental.equipment_id)
    )
    equipment = equipment_result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Set actual return date
    actual_end = request.actual_end_date or date.today()
    rental.actual_end_date = actual_end

    # Recalculate total amount based on actual rental period
    rental.total_amount = calculate_rental_amount(
        rental.daily_rate,
        rental.start_date,
        actual_end
    )

    # Update rental status
    rental.status = RentalStatus.RETURNED
    if request.return_notes:
        rental.return_notes = request.return_notes

    # Update equipment status
    old_status = equipment.status
    equipment.status = EquipmentStatus.IN_STOCK

    # Log equipment rental end
    await log_equipment_change(
        db=db,
        equipment_id=equipment.id,
        log_type=EquipmentLogType.RENTAL_END,
        description=f"Returned from {rental.customer.company_name} (Rental: {rental.rental_number})",
        old_value=f"Status: {old_status.value}",
        new_value=f"Status: {EquipmentStatus.IN_STOCK.value}",
        user_id=current_user.id,
        latitude=request.latitude,
        longitude=request.longitude,
    )

    await db.commit()
    await db.refresh(rental)

    return RentalResponse.model_validate(rental)


@router.post("/{rental_id}/cancel", response_model=RentalResponse)
async def cancel_rental(
    rental_id: int,
    request: RentalCancelRequest,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel rental (Manager+ only)
    Can only cancel rentals in DRAFT or CONFIRMED status
    """
    result = await db.execute(
        select(Rental).where(Rental.id == rental_id)
    )
    rental = result.scalar_one_or_none()

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental not found",
        )

    if rental.status not in [RentalStatus.DRAFT, RentalStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only cancel draft or confirmed rentals (current: {rental.status.value})",
        )

    # Update status
    rental.status = RentalStatus.CANCELLED
    rental.notes = f"{rental.notes}\n\nCancelled: {request.reason}" if rental.notes else f"Cancelled: {request.reason}"

    await db.commit()
    await db.refresh(rental)

    return RentalResponse.model_validate(rental)


# ==================== Rental Statistics ====================

@router.get("/overdue", response_model=RentalListResponse)
async def get_overdue_rentals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all overdue rentals
    Rentals that are ACTIVE but past expected_end_date
    """
    today = date.today()

    # Find active rentals past due date
    query = (
        select(Rental)
        .where(Rental.status == RentalStatus.ACTIVE)
        .where(Rental.expected_end_date < today)
        .order_by(Rental.expected_end_date)
    )

    result = await db.execute(query)
    overdue_rentals = result.scalars().all()

    # Update status to OVERDUE
    for rental in overdue_rentals:
        rental.status = RentalStatus.OVERDUE

    await db.commit()

    # Get count
    count = len(overdue_rentals)

    return RentalListResponse(
        rentals=[RentalResponse.model_validate(r) for r in overdue_rentals],
        total=count
    )
