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
    maintenance_notes: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    """Create equipment schema"""
    purchase_date: Optional[date] = None
    current_location_id: Optional[int] = None
    photo_url: Optional[str] = None
    manual_url: Optional[str] = None
    calibration_report_url: Optional[str] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None


class EquipmentUpdate(BaseModel):
    """Update equipment schema"""
    category: Optional[EquipmentCategory] = None
    manufacturer: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[EquipmentStatus] = None
    current_location_id: Optional[int] = None
    deployed_to: Optional[str] = Field(None, max_length=200)
    deployed_by: Optional[int] = None
    purchase_date: Optional[date] = None
    specifications: Optional[str] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    manual_url: Optional[str] = None
    calibration_report_url: Optional[str] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    maintenance_notes: Optional[str] = None


# ==================== Response Schemas ====================

class EquipmentResponse(BaseModel):
    """Equipment response schema"""
    id: int
    asset_code: str
    qr_code: str
    category: EquipmentCategory
    manufacturer: str
    model: str
    serial_number: Optional[str]
    status: EquipmentStatus
    current_location_id: Optional[int]
    deployed_to: Optional[str]
    deployed_by: Optional[int]
    purchase_date: Optional[date]
    photo_url: Optional[str]
    manual_url: Optional[str]
    calibration_report_url: Optional[str]
    last_maintenance_date: Optional[date]
    next_maintenance_date: Optional[date]
    maintenance_notes: Optional[str]
    specifications: Optional[str]
    notes: Optional[str]
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
