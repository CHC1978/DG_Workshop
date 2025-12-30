"""SubEquipment schemas"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.equipment import EquipmentStatus


# ==================== Base Schemas ====================

class SubEquipmentBase(BaseModel):
    """SubEquipment base schema"""
    component_name: str = Field(..., min_length=1, max_length=100, description="組件名稱")
    serial_number: Optional[str] = Field(None, max_length=100, description="序號")
    notes: Optional[str] = Field(None, max_length=500, description="備註")


class SubEquipmentCreate(SubEquipmentBase):
    """Create sub-equipment schema"""
    parent_equipment_id: int = Field(..., description="父設備 ID")


class SubEquipmentUpdate(BaseModel):
    """Update sub-equipment schema - all fields optional"""
    component_name: Optional[str] = Field(None, min_length=1, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[EquipmentStatus] = None
    notes: Optional[str] = Field(None, max_length=500)


# ==================== Response Schemas ====================

class SubEquipmentResponse(BaseModel):
    """SubEquipment response schema"""
    id: int
    parent_equipment_id: int
    asset_code: str
    qr_code: str
    component_name: str
    serial_number: Optional[str]
    status: EquipmentStatus
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubEquipmentDetailResponse(SubEquipmentResponse):
    """SubEquipment detail response with parent info"""
    parent_asset_code: Optional[str] = None
    parent_model: Optional[str] = None

    model_config = {"from_attributes": True}


class SubEquipmentListResponse(BaseModel):
    """SubEquipment list response schema"""
    sub_equipments: list[SubEquipmentResponse]
    total: int
