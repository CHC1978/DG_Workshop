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
    specifications: Optional[str] = Field(None, max_length=5000)
    notes: Optional[str] = Field(None, max_length=2000)
    maintenance_notes: Optional[str] = Field(None, max_length=2000)


class EquipmentCreate(EquipmentBase):
    """Create equipment schema"""
    model_code: Optional[str] = Field(None, max_length=50, description="Model code for Asset Code generation")
    purchase_date: Optional[date] = None
    current_location_id: Optional[int] = None

    # Parent-Child relationship
    parent_equipment_id: Optional[int] = Field(None, description="Parent equipment ID (for sub-components)")

    # Project and installation
    project_id: Optional[int] = Field(None, description="Associated project")
    installation_type: Optional[InstallationType] = Field(None, description="Installation type")
    installation_date: Optional[date] = Field(None, description="Installation date")
    installation_notes: Optional[str] = Field(None, max_length=2000, description="Installation notes")

    # Attachments
    photo_url: Optional[str] = Field(None, max_length=500)
    manual_url: Optional[str] = Field(None, max_length=500)
    calibration_report_url: Optional[str] = Field(None, max_length=500)

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

    # Parent-Child relationship
    parent_equipment_id: Optional[int] = Field(None, description="Parent equipment ID (for attaching/detaching)")

    # Project and installation
    project_id: Optional[int] = None
    installation_type: Optional[InstallationType] = None
    installation_date: Optional[date] = None
    installation_notes: Optional[str] = Field(None, max_length=2000)

    # Content
    specifications: Optional[str] = Field(None, max_length=5000)
    notes: Optional[str] = Field(None, max_length=2000)

    # Attachments
    photo_url: Optional[str] = Field(None, max_length=500)
    manual_url: Optional[str] = Field(None, max_length=500)
    calibration_report_url: Optional[str] = Field(None, max_length=500)

    # Maintenance
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    maintenance_notes: Optional[str] = Field(None, max_length=2000)


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

    # Parent-Child relationship
    parent_equipment_id: Optional[int]

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

    # Display fields for Parent Equipment (not from DB directly)
    parent_asset_code: Optional[str] = None
    parent_model: Optional[str] = None
    children_count: int = 0

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


class MaintenanceRecordRequest(BaseModel):
    """Request to add maintenance record to equipment"""
    maintenance_notes: str = Field(..., min_length=1, description="Maintenance details and notes")
    last_maintenance_date: Optional[date] = Field(None, description="Date of last maintenance")
    next_maintenance_date: Optional[date] = Field(None, description="Next scheduled maintenance date")


class LogAttachmentInfo(BaseModel):
    """Simplified attachment info for log list"""
    id: int
    file_url: str
    file_name: str
    file_type: str
    file_size: int

    model_config = {"from_attributes": True}


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

    # Attachments
    attachment_count: int = 0
    attachments: list[LogAttachmentInfo] = []

    model_config = {"from_attributes": True}


# ==================== Parent-Child Management Schemas ====================

class DetachFromParentRequest(BaseModel):
    """Request to detach equipment from parent (Manager+ only)"""
    new_location_id: int = Field(..., description="Target location after detach")
    new_status: EquipmentStatus = Field(..., description="Status after detach")
    notes: Optional[str] = Field(None, description="Reason for detaching")


class GroupMoveRequest(BaseModel):
    """Request to move equipment with all children as a group"""
    location_id: int = Field(..., description="Target location ID")
    include_children: bool = Field(True, description="Move children together with parent")
    notes: Optional[str] = Field(None, description="Notes for the move")


class SyncChildrenStatusRequest(BaseModel):
    """Request to sync children status with parent"""
    new_status: EquipmentStatus = Field(..., description="New status to apply")
    include_children: bool = Field(True, description="Apply to children as well")
    notes: Optional[str] = Field(None, description="Notes for status change")


# Forward reference for Location
from app.schemas.location import LocationResponse
EquipmentDetailResponse.model_rebuild()
