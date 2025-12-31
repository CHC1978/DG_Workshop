"""Equipment schemas"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.equipment import EquipmentCategory, EquipmentStatus, InstallationType


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
    model_code: Optional[str] = Field(None, max_length=50, description="Model code for Asset Code generation")
    purchase_date: Optional[date] = None
    current_location_id: Optional[int] = None

    # Project and installation
    project_id: Optional[int] = Field(None, description="Associated project")
    installation_type: Optional[InstallationType] = Field(None, description="Installation type")
    installation_date: Optional[date] = Field(None, description="Installation date")
    installation_notes: Optional[str] = Field(None, description="Installation notes")

    # Attachments
    photo_url: Optional[str] = None
    manual_url: Optional[str] = None
    calibration_report_url: Optional[str] = None

    # Maintenance
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None


class EquipmentUpdate(BaseModel):
    """Update equipment schema"""
    category: Optional[EquipmentCategory] = None
    manufacturer: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    model_code: Optional[str] = Field(None, max_length=50)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[EquipmentStatus] = None
    current_location_id: Optional[int] = None
    deployed_to: Optional[str] = Field(None, max_length=200)
    deployed_by: Optional[int] = None
    purchase_date: Optional[date] = None

    # Project and installation
    project_id: Optional[int] = None
    installation_type: Optional[InstallationType] = None
    installation_date: Optional[date] = None
    installation_notes: Optional[str] = None

    # Content
    specifications: Optional[str] = None
    notes: Optional[str] = None

    # Attachments
    photo_url: Optional[str] = None
    manual_url: Optional[str] = None
    calibration_report_url: Optional[str] = None

    # Maintenance
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
    model_code: Optional[str]
    serial_number: Optional[str]
    status: EquipmentStatus
    current_location_id: Optional[int]
    deployed_to: Optional[str]
    deployed_by: Optional[int]
    purchase_date: Optional[date]

    # Project and installation
    project_id: Optional[int]
    installation_type: Optional[InstallationType]
    installation_date: Optional[date]
    installation_notes: Optional[str]

    # Attachments
    photo_url: Optional[str]
    manual_url: Optional[str]
    calibration_report_url: Optional[str]

    # Maintenance
    last_maintenance_date: Optional[date]
    next_maintenance_date: Optional[date]
    maintenance_notes: Optional[str]

    # Content
    specifications: Optional[str]
    notes: Optional[str]

    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Display fields for Location and Project (not from DB directly)
    current_location_name: Optional[str] = None
    current_location_type: Optional[str] = None
    project_code: Optional[str] = None
    project_name: Optional[str] = None

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

class EquipmentLogUpdateRequest(BaseModel):
    """Equipment log update request - only description and GPS can be edited"""
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


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
    created_by_username: Optional[str] = None  # Username of who created the log

    # Edit tracking
    edited_at: Optional[datetime] = None
    edited_by: Optional[int] = None
    edited_by_username: Optional[str] = None
    edit_count: int = 0
    is_edited: bool = False  # Computed: edit_count > 0

    # Current equipment location and project info (not historical)
    current_location_name: Optional[str] = None
    current_location_type: Optional[str] = None
    project_code: Optional[str] = None
    project_name: Optional[str] = None

    model_config = {"from_attributes": True}


# Forward reference for Location
from app.schemas.location import LocationResponse
EquipmentDetailResponse.model_rebuild()
