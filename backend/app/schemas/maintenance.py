"""Maintenance schemas"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


# ==================== Base Schemas ====================

class MaintenanceBase(BaseModel):
    """Maintenance base schema"""
    equipment_id: int
    maintenance_date: date
    next_due_date: date
    provider: str = Field(..., min_length=1, max_length=200)
    service_type: Optional[str] = Field(None, max_length=100)
    cost: Optional[float] = Field(None, ge=0)
    report_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


class MaintenanceCreate(MaintenanceBase):
    """Create maintenance schema"""
    pass


class MaintenanceUpdate(BaseModel):
    """Update maintenance schema"""
    equipment_id: Optional[int] = None
    maintenance_date: Optional[date] = None
    next_due_date: Optional[date] = None
    provider: Optional[str] = Field(None, min_length=1, max_length=200)
    service_type: Optional[str] = Field(None, max_length=100)
    cost: Optional[float] = Field(None, ge=0)
    report_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


# ==================== Response Schemas ====================

class MaintenanceResponse(BaseModel):
    """Maintenance response schema"""
    id: int
    equipment_id: int
    maintenance_date: date
    next_due_date: date
    provider: str
    service_type: Optional[str]
    cost: Optional[float]
    report_url: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MaintenanceListResponse(BaseModel):
    """Maintenance list response schema"""
    maintenances: list[MaintenanceResponse]
    total: int


class MaintenanceDetailResponse(MaintenanceResponse):
    """Maintenance detail response with equipment info"""
    equipment: Optional[dict] = None  # EquipmentResponse

    model_config = {"from_attributes": True}


class MaintenanceDueSoonResponse(BaseModel):
    """Maintenance due soon response"""
    maintenance: MaintenanceResponse
    equipment_asset_code: str
    equipment_name: str
    days_until_due: int
    is_overdue: bool
