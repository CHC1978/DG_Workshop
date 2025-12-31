"""User schemas"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


# ==================== Base Schemas ====================

class UserBase(BaseModel):
    """User base schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Create user schema"""
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    """Update user schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    """Update password schema"""
    old_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)


class AdminPasswordResetRequest(BaseModel):
    """Admin reset user password schema (no old password required)"""
    new_password: str = Field(..., min_length=8, max_length=128, description="New password to set")


class AdminToggle2FARequest(BaseModel):
    """Admin toggle 2FA for user schema"""
    enabled: bool = Field(..., description="Enable or disable 2FA")


# ==================== Response Schemas ====================

class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: UserRole
    totp_enabled: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """User list response schema"""
    users: list[UserResponse]
    total: int
