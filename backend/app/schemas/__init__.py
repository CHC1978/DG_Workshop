"""Schemas module"""
from app.schemas.auth import (
    LoginStep1Request,
    LoginStep1Response,
    LoginStep2Request,
    LoginStep2Response,
    Setup2FAResponse,
    Confirm2FARequest,
    Confirm2FAResponse,
    Reset2FAResponse,
    TokenPayload,
    CurrentUser,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    UserListResponse,
)
from app.schemas.equipment import (
    EquipmentBase,
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
    EquipmentDetailResponse,
    QRCodeResponse,
    EquipmentLogResponse,
)
from app.schemas.location import (
    LocationBase,
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationListResponse,
    LocationDetailResponse,
)

__all__ = [
    # Auth
    "LoginStep1Request",
    "LoginStep1Response",
    "LoginStep2Request",
    "LoginStep2Response",
    "Setup2FAResponse",
    "Confirm2FARequest",
    "Confirm2FAResponse",
    "Reset2FAResponse",
    "TokenPayload",
    "CurrentUser",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPasswordUpdate",
    "UserResponse",
    "UserListResponse",
    # Equipment
    "EquipmentBase",
    "EquipmentCreate",
    "EquipmentUpdate",
    "EquipmentResponse",
    "EquipmentListResponse",
    "EquipmentDetailResponse",
    "QRCodeResponse",
    "EquipmentLogResponse",
    # Location
    "LocationBase",
    "LocationCreate",
    "LocationUpdate",
    "LocationResponse",
    "LocationListResponse",
    "LocationDetailResponse",
]