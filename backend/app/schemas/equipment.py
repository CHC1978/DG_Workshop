"""Equipment schemas"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.equipment import EquipmentCategory, EquipmentStatus


# ==================== Base Schemas ====================

class EquipmentBase(BaseModel):
    """Equipment base schema"""
    category: EquipmentCategory
    manufacturer: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    specifications: Optional[str] = None
    notes: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    """Create equipment schema"""
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    rental_daily_rate: Optional[float] = Field(None, ge=0)
    current_location_id: Optional[int] = None


class EquipmentUpdate(BaseModel):
    """Update equipment schema"""
    category: Optional[EquipmentCategory] = None
    manufacturer: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[EquipmentStatus] = None
    current_location_id: Optional[int] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    rental_daily_rate: Optional[float] = Field(None, ge=0)
    specifications: Optional[str] = None
    notes: Optional[str] = None


# ==================== Response Schemas ====================

class EquipmentResponse(EquipmentBase):
    """Equipment response schema"""
    id: int
    asset_code: str
    qr_code: str
    status: EquipmentStatus
    current_location_id: Optional[int]
    purchase_date: Optional[date]
    purchase_price: Optional[float]
    rental_daily_rate: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EquipmentListResponse(BaseModel):
    """Equipment list response schema"""
    equipments: list[EquipmentResponse]
    total: int


class EquipmentDetailResponse(EquipmentResponse):
    """Equipment detail response with relations"""
    current_location: Optional["LocationResponse"] = None

    model_config = {"from_attributes": True}


# ==================== QR Code Schemas ====================

class QRCodeResponse(BaseModel):
    """QR Code response schema"""
    asset_code: str
    qr_code_url: str
    qr_code_base64: str


# ==================== Equipment Log Schemas ====================

class EquipmentLogResponse(BaseModel):
    """Equipment log response schema"""
    id: int
    equipment_id: int
    log_type: str
    old_value: Optional[str]
    new_value: Optional[str]
    description: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    created_by: Optional[int]

    model_config = {"from_attributes": True}


# Forward reference for Location
from app.schemas.location import LocationResponse
EquipmentDetailResponse.model_rebuild()
