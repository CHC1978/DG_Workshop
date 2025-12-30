"""Customer management API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager
from app.models.user import User
from app.models.customer import Customer
from app.models.rental import Rental, RentalStatus
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    CustomerDetailResponse,
)
from app.schemas.rental import RentalResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


# ==================== CRUD Operations ====================

@router.get("", response_model=CustomerListResponse)
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all customers with search and pagination
    """
    query = select(Customer).where(Customer.is_active == True)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Customer.company_name.like(search_pattern),
                Customer.contact_person.like(search_pattern),
                Customer.tax_id.like(search_pattern),
                Customer.phone.like(search_pattern),
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Customer.company_name)
    result = await db.execute(query)
    customers = result.scalars().all()

    return CustomerListResponse(
        customers=[CustomerResponse.model_validate(c) for c in customers],
        total=total
    )


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new customer (Manager+ only)
    """
    # Check if tax_id already exists (if provided)
    if customer_data.tax_id:
        result = await db.execute(
            select(Customer).where(Customer.tax_id == customer_data.tax_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tax ID already exists",
            )

    # Create customer
    new_customer = Customer(
        company_name=customer_data.company_name,
        tax_id=customer_data.tax_id,
        contact_person=customer_data.contact_person,
        phone=customer_data.phone,
        email=customer_data.email,
        address=customer_data.address,
        notes=customer_data.notes,
        is_active=True,
    )

    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)

    return CustomerResponse.model_validate(new_customer)


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get customer by ID with rental statistics
    """
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    # Get rental counts
    total_rentals_result = await db.execute(
        select(func.count(Rental.id))
        .where(Rental.customer_id == customer_id)
    )
    rental_count = total_rentals_result.scalar()

    active_rentals_result = await db.execute(
        select(func.count(Rental.id))
        .where(Rental.customer_id == customer_id)
        .where(Rental.status.in_([RentalStatus.CONFIRMED, RentalStatus.ACTIVE]))
    )
    active_rental_count = active_rentals_result.scalar()

    # Build response
    response = CustomerDetailResponse.model_validate(customer)
    response.rental_count = rental_count
    response.active_rental_count = active_rental_count

    return response


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update customer (Manager+ only)
    """
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    # Check if new tax_id already exists
    if customer_data.tax_id and customer_data.tax_id != customer.tax_id:
        result = await db.execute(
            select(Customer).where(
                Customer.tax_id == customer_data.tax_id,
                Customer.id != customer_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tax ID already exists",
            )

    # Update fields
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(customer, field):
            setattr(customer, field, value)

    await db.commit()
    await db.refresh(customer)

    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (deactivate) customer (Manager+ only)
    Uses soft delete by setting is_active to False
    """
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    # Check if customer has active rentals
    active_rentals_result = await db.execute(
        select(func.count(Rental.id))
        .where(Rental.customer_id == customer_id)
        .where(Rental.status.in_([RentalStatus.CONFIRMED, RentalStatus.ACTIVE]))
    )
    active_rental_count = active_rentals_result.scalar()

    if active_rental_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete customer with {active_rental_count} active rentals",
        )

    # Soft delete
    customer.is_active = False
    await db.commit()


# ==================== Customer Rentals ====================

@router.get("/{customer_id}/rentals", response_model=list[RentalResponse])
async def get_customer_rentals(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all rentals for a customer
    """
    # Verify customer exists
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    # Get rentals
    query = (
        select(Rental)
        .where(Rental.customer_id == customer_id)
        .order_by(Rental.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    rentals = result.scalars().all()

    return [RentalResponse.model_validate(r) for r in rentals]
