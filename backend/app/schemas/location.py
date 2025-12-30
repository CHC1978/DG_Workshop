"""Location schemas"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.location import LocationType


# ==================== Base Schemas ====================

class LocationBase(BaseModel):
    """Location base schema"""
    name: str = Field(..., min_length=1, max_length=100)
    location_type: LocationType
    code: Optional[str] = Field(None, max_length=50)
    imo_number: Optional[str] = Field(None, max_length=20)
    call_sign: Optional[str] = Field(None, max_length=20)
    owner_company: Optional[str] = Field(None, max_length=100)


class LocationCreate(LocationBase):
    """Create location schema"""
    pass


class LocationUpdate(BaseModel):
    """Update location schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location_type: Optional[LocationType] = None
    code: Optional[str] = Field(None, max_length=50)
    imo_number: Optional[str] = Field(None, max_length=20)
    call_sign: Optional[str] = Field(None, max_length=20)
    owner_company: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


# ==================== Response Schemas ====================

class LocationResponse(LocationBase):
    """Location response schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LocationListResponse(BaseModel):
    """Location list response schema"""
    locations: list[LocationResponse]
    total: int


class LocationDetailResponse(LocationResponse):
    """Location detail response with equipment count"""
    equipment_count: int = 0

    model_config = {"from_attributes": True}
