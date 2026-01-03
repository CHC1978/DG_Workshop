"""Location schemas"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.location import LocationType


# ==================== Base Schemas ====================

class LocationBase(BaseModel):
    """Location base schema"""
    name: str = Field(..., min_length=1, max_length=100)
    location_type: LocationType
    code: Optional[str] = Field(None, max_length=50)

    # Vessel identifiers (legacy)
    imo_number: Optional[str] = Field(None, max_length=20)
    call_sign: Optional[str] = Field(None, max_length=20)
    owner_company: Optional[str] = Field(None, max_length=100)

    # Vessel identifiers (new - multiple options)
    vessel_mmsi: Optional[str] = Field(None, max_length=9, description="Vessel MMSI (9 digits)")
    vessel_national_id: Optional[str] = Field(None, max_length=30, description="Vessel National Registration ID")
    vessel_internal_code: Optional[str] = Field(None, max_length=20, description="Vessel Internal Code")

    # Vessel information
    vessel_name: Optional[str] = Field(None, max_length=100, description="Vessel Name")
    vessel_flag: Optional[str] = Field(None, max_length=50, description="Vessel Flag/Country")
    vessel_type: Optional[str] = Field(None, max_length=50, description="Vessel Type")
    vessel_owner: Optional[str] = Field(None, max_length=100, description="Vessel Owner")

    # Person fields
    person_name: Optional[str] = Field(None, max_length=100, description="Person Name")
    person_contact: Optional[str] = Field(None, max_length=100, description="Person Contact Info")
    employee_id: Optional[str] = Field(None, max_length=30, description="Employee ID")
    department: Optional[str] = Field(None, max_length=100, description="Department")

    # Photo (for Vessel and Person)
    photo_url: Optional[str] = Field(None, max_length=500, description="Photo URL")

    # Warehouse fields
    address: Optional[str] = Field(None, max_length=500, description="Warehouse Address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone Number")
    email: Optional[str] = Field(None, max_length=100, description="Email Address")

    # Contact person (舊：reference to another Location with type=person，待遷移後移除)
    contact_person_id: Optional[int] = Field(None, description="Contact Person Location ID (deprecated)")

    # Contact user (新：reference to User，Person 合併到 User 後使用)
    contact_user_id: Optional[int] = Field(None, description="Contact User ID")

    # Project association
    current_project_id: Optional[int] = Field(None, description="Current Project ID")


class LocationCreate(LocationBase):
    """Create location schema"""

    @model_validator(mode='after')
    def validate_vessel_identifiers(self):
        """Validate that VESSEL type has at least one identifier"""
        if self.location_type == LocationType.VESSEL:
            # Get all vessel identifier fields
            identifiers = [
                self.imo_number,
                self.vessel_mmsi,
                self.vessel_national_id,
                self.vessel_internal_code,
                self.call_sign
            ]
            # Check if at least one identifier is provided
            if not any(identifiers):
                raise ValueError(
                    'Vessel location must have at least one identifier: '
                    'imo_number, vessel_mmsi, vessel_national_id, vessel_internal_code, or call_sign'
                )
        return self


class LocationUpdate(BaseModel):
    """Update location schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location_type: Optional[LocationType] = None
    code: Optional[str] = Field(None, max_length=50)

    # Vessel identifiers (legacy)
    imo_number: Optional[str] = Field(None, max_length=20)
    call_sign: Optional[str] = Field(None, max_length=20)
    owner_company: Optional[str] = Field(None, max_length=100)

    # Vessel identifiers (new)
    vessel_mmsi: Optional[str] = Field(None, max_length=9)
    vessel_national_id: Optional[str] = Field(None, max_length=30)
    vessel_internal_code: Optional[str] = Field(None, max_length=20)

    # Vessel information
    vessel_name: Optional[str] = Field(None, max_length=100)
    vessel_flag: Optional[str] = Field(None, max_length=50)
    vessel_type: Optional[str] = Field(None, max_length=50)
    vessel_owner: Optional[str] = Field(None, max_length=100)

    # Person fields
    person_name: Optional[str] = Field(None, max_length=100)
    person_contact: Optional[str] = Field(None, max_length=100)
    employee_id: Optional[str] = Field(None, max_length=30)
    department: Optional[str] = Field(None, max_length=100)

    # Photo (for Vessel and Person)
    photo_url: Optional[str] = Field(None, max_length=500)

    # Warehouse fields
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)

    # Contact person (舊，待遷移後移除)
    contact_person_id: Optional[int] = None

    # Contact user (新)
    contact_user_id: Optional[int] = None

    # Project association
    current_project_id: Optional[int] = None

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
    """Location detail response with equipment count and project info"""
    equipment_count: int = 0
    project_name: Optional[str] = None
    project_code: Optional[str] = None
    contact_person_name: Optional[str] = None  # 舊欄位，待遷移後移除
    contact_user_name: Optional[str] = None  # 新欄位，Person 合併到 User 後使用

    model_config = {"from_attributes": True}
