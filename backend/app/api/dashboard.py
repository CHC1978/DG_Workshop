"""Dashboard statistics and alerts API"""
from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.equipment import Equipment, EquipmentStatus
from app.models.rental import Rental, RentalStatus
from app.models.calibration import Calibration

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class MaintenanceAlert(BaseModel):
    equipment_id: int
    asset_code: str
    manufacturer: str
    model: str
    next_maintenance_date: date
    days_until_due: int
    is_overdue: bool


class CalibrationAlert(BaseModel):
    equipment_id: int
    asset_code: str
    manufacturer: str
    model: str
    calibration_id: int
    next_due_date: date
    days_until_due: int
    is_overdue: bool


class RentalAlert(BaseModel):
    rental_id: int
    rental_number: str
    equipment_asset_code: str
    customer_company: str
    expected_end_date: date
    days_overdue: int


class DashboardStats(BaseModel):
    total_equipment: int
    in_stock: int
    deployed: int
    rented: int
    in_repair: int
    active_rentals: int
    maintenance_due_soon: int
    calibration_due_soon: int
    overdue_rentals: int


class DashboardAlerts(BaseModel):
    maintenance_alerts: List[MaintenanceAlert]
    calibration_alerts: List[CalibrationAlert]
    overdue_rentals: List[RentalAlert]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics"""
    # Total equipment
    total_result = await db.execute(
        select(func.count(Equipment.id)).where(Equipment.is_active == True)
    )
    total_equipment = total_result.scalar()

    # Count by status
    in_stock_result = await db.execute(
        select(func.count(Equipment.id)).where(
            Equipment.status == EquipmentStatus.IN_STOCK,
            Equipment.is_active == True
        )
    )
    in_stock = in_stock_result.scalar()

    deployed_result = await db.execute(
        select(func.count(Equipment.id)).where(
            Equipment.status == EquipmentStatus.DEPLOYED,
            Equipment.is_active == True
        )
    )
    deployed = deployed_result.scalar()

    rented_result = await db.execute(
        select(func.count(Equipment.id)).where(
            Equipment.status == EquipmentStatus.RENTED,
            Equipment.is_active == True
        )
    )
    rented = rented_result.scalar()

    in_repair_result = await db.execute(
        select(func.count(Equipment.id)).where(
            Equipment.status == EquipmentStatus.REPAIR,
            Equipment.is_active == True
        )
    )
    in_repair = in_repair_result.scalar()

    # Active rentals
    active_rentals_result = await db.execute(
        select(func.count(Rental.id)).where(
            Rental.status.in_([RentalStatus.CONFIRMED, RentalStatus.ACTIVE])
        )
    )
    active_rentals = active_rentals_result.scalar()

    # Maintenance due soon (30 days)
    thirty_days_from_now = date.today() + timedelta(days=30)
    maintenance_due_result = await db.execute(
        select(func.count(Equipment.id)).where(
            Equipment.next_maintenance_date <= thirty_days_from_now,
            Equipment.next_maintenance_date.isnot(None),
            Equipment.is_active == True
        )
    )
    maintenance_due_soon = maintenance_due_result.scalar()

    # Calibration due soon (30 days)
    calibration_due_result = await db.execute(
        select(func.count(Calibration.id)).where(
            Calibration.next_due_date <= thirty_days_from_now
        )
    )
    calibration_due_soon = calibration_due_result.scalar()

    # Overdue rentals
    today = date.today()
    overdue_result = await db.execute(
        select(func.count(Rental.id)).where(
            Rental.status == RentalStatus.ACTIVE,
            Rental.expected_end_date < today
        )
    )
    overdue_rentals = overdue_result.scalar()

    return DashboardStats(
        total_equipment=total_equipment,
        in_stock=in_stock,
        deployed=deployed,
        rented=rented,
        in_repair=in_repair,
        active_rentals=active_rentals,
        maintenance_due_soon=maintenance_due_soon,
        calibration_due_soon=calibration_due_soon,
        overdue_rentals=overdue_rentals
    )


@router.get("/alerts", response_model=DashboardAlerts)
async def get_dashboard_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard alerts for time-sensitive items"""
    today = date.today()
    thirty_days = today + timedelta(days=30)

    # Maintenance alerts
    maintenance_query = select(Equipment).where(
        Equipment.next_maintenance_date <= thirty_days,
        Equipment.next_maintenance_date.isnot(None),
        Equipment.is_active == True
    ).order_by(Equipment.next_maintenance_date)

    maintenance_result = await db.execute(maintenance_query)
    maintenance_equipment = maintenance_result.scalars().all()

    maintenance_alerts = []
    for eq in maintenance_equipment:
        days_until = (eq.next_maintenance_date - today).days
        maintenance_alerts.append(MaintenanceAlert(
            equipment_id=eq.id,
            asset_code=eq.asset_code,
            manufacturer=eq.manufacturer,
            model=eq.model,
            next_maintenance_date=eq.next_maintenance_date,
            days_until_due=days_until,
            is_overdue=days_until < 0
        ))

    # Calibration alerts
    calibration_query = select(Calibration, Equipment).join(
        Equipment, Calibration.equipment_id == Equipment.id
    ).where(
        Calibration.next_due_date <= thirty_days
    ).order_by(Calibration.next_due_date)

    calibration_result = await db.execute(calibration_query)
    calibration_pairs = calibration_result.all()

    calibration_alerts = []
    for cal, eq in calibration_pairs:
        days_until = (cal.next_due_date - today).days
        calibration_alerts.append(CalibrationAlert(
            equipment_id=eq.id,
            asset_code=eq.asset_code,
            manufacturer=eq.manufacturer,
            model=eq.model,
            calibration_id=cal.id,
            next_due_date=cal.next_due_date,
            days_until_due=days_until,
            is_overdue=days_until < 0
        ))

    # Overdue rentals
    from app.models.customer import Customer

    overdue_query = select(Rental, Equipment, Customer).join(
        Equipment, Rental.equipment_id == Equipment.id
    ).join(
        Customer, Rental.customer_id == Customer.id
    ).where(
        Rental.status == RentalStatus.ACTIVE,
        Rental.expected_end_date < today
    ).order_by(Rental.expected_end_date)

    overdue_result = await db.execute(overdue_query)
    overdue_tuples = overdue_result.all()

    rental_alerts = []
    for rental, equipment, customer in overdue_tuples:
        days_overdue = (today - rental.expected_end_date).days
        rental_alerts.append(RentalAlert(
            rental_id=rental.id,
            rental_number=rental.rental_number,
            equipment_asset_code=equipment.asset_code,
            customer_company=customer.company_name,
            expected_end_date=rental.expected_end_date,
            days_overdue=days_overdue
        ))

    return DashboardAlerts(
        maintenance_alerts=maintenance_alerts,
        calibration_alerts=calibration_alerts,
        overdue_rentals=rental_alerts
    )


class RecentActivity(BaseModel):
    """Recent activity item"""
    id: int
    equipment_id: int
    asset_code: str
    manufacturer: str
    model: str
    log_type: str
    description: str
    created_by_username: Optional[str]
    created_at: datetime


@router.get("/recent-activities", response_model=List[RecentActivity])
async def get_recent_activities(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent equipment activities"""
    from app.models.equipment_log import EquipmentLog

    # Query recent logs with equipment and user info
    query = (
        select(EquipmentLog, Equipment, User)
        .join(Equipment, EquipmentLog.equipment_id == Equipment.id)
        .outerjoin(User, EquipmentLog.created_by == User.id)
        .order_by(EquipmentLog.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    log_tuples = result.all()

    activities = []
    for log, equipment, user in log_tuples:
        activities.append(RecentActivity(
            id=log.id,
            equipment_id=equipment.id,
            asset_code=equipment.asset_code,
            manufacturer=equipment.manufacturer,
            model=equipment.model,
            log_type=log.log_type.value,
            description=log.description or "",
            created_by_username=user.username if user else None,
            created_at=log.created_at
        ))

    return activities
