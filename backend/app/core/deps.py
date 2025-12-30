"""依賴注入與權限檢查"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    取得當前登入使用者

    從 Authorization header 解析 JWT token 並取得使用者資訊
    """
    token = credentials.credentials

    # 解碼 token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證憑證",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 取得 user_id (convert from string to int)
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證憑證",
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證憑證",
        )

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證憑證",
        )

    # 從資料庫取得使用者
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者不存在",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="使用者帳號已停用",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """確保是啟用狀態的使用者"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="使用者帳號已停用"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    權限檢查裝飾器工廠

    Usage:
        @router.get("/admin-only")
        async def admin_only(user: User = Depends(require_role(UserRole.ADMIN))):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要角色: {', '.join(r.value for r in allowed_roles)}"
            )
        return current_user

    return role_checker


async def get_user_from_temp_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get user from temporary token (for 2FA setup)
    Accepts temp token from login step 1
    """
    token = credentials.credentials
    print(f"[DEBUG] get_user_from_temp_token called with token: {token[:50]}...")

    # Decode token
    payload = decode_token(token)
    print(f"[DEBUG] Decoded payload: {payload}")

    if payload is None:
        print("[DEBUG] Payload is None - token decode failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Verify it's a temp token
    token_type = payload.get("type")
    print(f"[DEBUG] Token type: {token_type}")

    if token_type != "temp":
        print(f"[DEBUG] Wrong token type. Expected 'temp', got '{token_type}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected 'temp', got '{token_type}'. Temporary token required.",
        )

    # Get user_id (convert from string to int)
    user_id_str = payload.get("sub")
    print(f"[DEBUG] User ID string from token: {user_id_str}")

    if user_id_str is None:
        print("[DEBUG] No user_id in payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(user_id_str)
        print(f"[DEBUG] Converted to int: {user_id}")
    except (ValueError, TypeError) as e:
        print(f"[DEBUG] Failed to convert user_id to int: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    if user_id is None:
        print("[DEBUG] No user_id in payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    print(f"[DEBUG] User found: {user is not None}")

    if user is None:
        print("[DEBUG] User not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        print("[DEBUG] User is not active")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    print(f"[DEBUG] Successfully authenticated user: {user.username}")
    return user


# 預定義的權限檢查依賴
require_admin = require_role(UserRole.ADMIN)
require_manager = require_role(UserRole.ADMIN, UserRole.MANAGER)
require_operator = require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.OPERATOR)
