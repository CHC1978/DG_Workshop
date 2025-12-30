"""Authentication schemas"""
from typing import Optional
from pydantic import BaseModel, Field


# ==================== Login Schemas ====================

class LoginStep1Request(BaseModel):
    """Step 1: Username and password login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)


class LoginStep1Response(BaseModel):
    """Step 1 response: Temporary token"""
    temp_token: str
    totp_required: bool
    message: str = "Please provide TOTP code"


class LoginStep2Request(BaseModel):
    """Step 2: TOTP verification"""
    temp_token: str
    totp_code: str = Field(..., min_length=6, max_length=6)


class LoginStep2Response(BaseModel):
    """Step 2 response: Access token"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


# ==================== 2FA Setup Schemas ====================

class Setup2FAResponse(BaseModel):
    """2FA setup response"""
    secret: str
    qr_code: str  # Base64 encoded QR code image
    backup_codes: list[str]
    message: str = "Scan QR code with authenticator app"


class Confirm2FARequest(BaseModel):
    """Confirm 2FA setup"""
    totp_code: str = Field(..., min_length=6, max_length=6)


class Confirm2FAResponse(BaseModel):
    """Confirm 2FA response"""
    success: bool
    message: str


class Reset2FAResponse(BaseModel):
    """Reset 2FA response"""
    success: bool
    message: str


# ==================== Token Schemas ====================

class TokenPayload(BaseModel):
    """Token payload"""
    sub: int  # user_id
    username: Optional[str] = None
    role: Optional[str] = None
    type: str = "access"  # access or temp


# ==================== Current User Schema ====================

class CurrentUser(BaseModel):
    """Current authenticated user"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    totp_enabled: bool
    is_active: bool

    model_config = {"from_attributes": True}
