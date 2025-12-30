"""Rental schemas"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.rental import RentalStatus


# ==================== Base Schemas ====================

class RentalBase(BaseModel):
    """Rental base schema"""
    equipment_id: int
    customer_id: int
    start_date: date
    expected_end_date: date
    notes: Optional[str] = None


class RentalCreate(RentalBase):
    """Create rental schema"""
    pass


class RentalUpdate(BaseModel):
    """Update rental schema"""
    equipment_id: Optional[int] = None
    customer_id: Optional[int] = None
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[RentalStatus] = None
    notes: Optional[str] = None
    delivery_notes: Optional[str] = None
    return_notes: Optional[str] = None


# ==================== Action Schemas ====================

class RentalConfirmRequest(BaseModel):
    """Confirm rental request"""
    notes: Optional[str] = None


class RentalDeliverRequest(BaseModel):
    """Deliver rental request"""
    delivery_notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RentalReturnRequest(BaseModel):
    """Return rental request"""
    actual_end_date: Optional[date] = None
    return_notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RentalCancelRequest(BaseModel):
    """Cancel rental request"""
    reason: str = Field(..., min_length=1)


# ==================== Response Schemas ====================

class RentalResponse(RentalBase):
    """Rental response schema"""
    id: int
    rental_number: str
    actual_end_date: Optional[date]
    status: RentalStatus
    delivery_notes: Optional[str]
    return_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RentalListResponse(BaseModel):
    """Rental list response schema"""
    rentals: list[RentalResponse]
    total: int


class RentalDetailResponse(RentalResponse):
    """Rental detail response with related data"""
    equipment: Optional[dict] = None  # EquipmentResponse
    customer: Optional[dict] = None   # CustomerResponse

    model_config = {"from_attributes": True}
