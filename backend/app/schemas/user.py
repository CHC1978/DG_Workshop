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
    # Person 資訊欄位（從 Location type=person 合併）
    employee_id: Optional[str] = Field(None, max_length=30, description="員工編號")
    department: Optional[str] = Field(None, max_length=100, description="部門")
    phone: Optional[str] = Field(None, max_length=50, description="電話")


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
    # Person 資訊欄位
    employee_id: Optional[str] = Field(None, max_length=30)
    department: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)


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
    photo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserStaffResponse(BaseModel):
    """簡化的使用者資訊（用於聯繫人/負責人下拉選單）"""
    id: int
    username: str
    full_name: str
    employee_id: Optional[str] = None
    department: Optional[str] = None
    photo_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """User list response schema"""
    users: list[UserResponse]
    total: int
