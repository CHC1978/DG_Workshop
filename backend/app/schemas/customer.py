"""Customer schemas"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ==================== Base Schemas ====================

class CustomerBase(BaseModel):
    """Customer base schema"""
    company_name: str = Field(..., min_length=1, max_length=200)
    tax_id: Optional[str] = Field(None, max_length=50)
    contact_person: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


class CustomerCreate(CustomerBase):
    """Create customer schema"""
    pass


class CustomerUpdate(BaseModel):
    """Update customer schema"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    tax_id: Optional[str] = Field(None, max_length=50)
    contact_person: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None


# ==================== Response Schemas ====================

class CustomerResponse(CustomerBase):
    """Customer response schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListResponse(BaseModel):
    """Customer list response schema"""
    customers: list[CustomerResponse]
    total: int


class CustomerDetailResponse(CustomerResponse):
    """Customer detail response with rental count"""
    rental_count: int = 0
    active_rental_count: int = 0

    model_config = {"from_attributes": True}
