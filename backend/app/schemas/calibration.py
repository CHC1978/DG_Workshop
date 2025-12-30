"""Calibration schemas"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


# ==================== Base Schemas ====================

class CalibrationBase(BaseModel):
    """Calibration base schema"""
    equipment_id: int
    calibration_date: date
    next_due_date: date
    provider: str = Field(..., min_length=1, max_length=200)
    certificate_number: Optional[str] = Field(None, max_length=100)
    cost: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class CalibrationCreate(CalibrationBase):
    """Create calibration schema"""
    pass


class CalibrationUpdate(BaseModel):
    """Update calibration schema"""
    equipment_id: Optional[int] = None
    calibration_date: Optional[date] = None
    next_due_date: Optional[date] = None
    provider: Optional[str] = Field(None, min_length=1, max_length=200)
    certificate_number: Optional[str] = Field(None, max_length=100)
    cost: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


# ==================== Response Schemas ====================

class CalibrationResponse(CalibrationBase):
    """Calibration response schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CalibrationListResponse(BaseModel):
    """Calibration list response schema"""
    calibrations: list[CalibrationResponse]
    total: int


class CalibrationDetailResponse(CalibrationResponse):
    """Calibration detail response with equipment info"""
    equipment: Optional[dict] = None  # EquipmentResponse

    model_config = {"from_attributes": True}


class CalibrationDueSoonResponse(BaseModel):
    """Calibration due soon response"""
    calibration: CalibrationResponse
    equipment_asset_code: str
    equipment_name: str
    days_until_due: int
    is_overdue: bool
