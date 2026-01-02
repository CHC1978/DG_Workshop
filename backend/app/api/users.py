"""User management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.core.deps import get_current_user, require_admin
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    AdminPasswordResetRequest,
    AdminToggle2FARequest,
    UserResponse,
    UserListResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])

# 從 main.py 獲取 limiter
from app.main import limiter


# ==================== User CRUD ====================

@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users (requires authentication)
    Admin can see all users, others can only see active users
    """
    query = select(User)

    # Non-admin users can only see active users
    if current_user.role != UserRole.ADMIN:
        query = query.where(User.is_active == True)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated users
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_user(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create new user (Admin only)
    """
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        totp_enabled=False,
        is_active=True,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse.model_validate(new_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user by ID
    Users can only view their own profile, Admin can view all
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check permission
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
        )

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user
    Users can update their own profile (except role), Admin can update all
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check permission
    is_self = current_user.id == user_id
    is_admin = current_user.role == UserRole.ADMIN

    if not is_self and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    # Update fields
    if user_data.email is not None:
        # Check if new email already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
        user.email = user_data.email

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    # Only admin can change role and is_active
    if is_admin:
        if user_data.role is not None:
            user.role = user_data.role
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete user permanently (Admin only)
    WARNING: This is a hard delete - user will be permanently removed from database
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # Hard delete - permanently remove from database
    await db.delete(user)
    await db.commit()


# ==================== Password Management ====================

@router.post("/{user_id}/password", response_model=dict)
@limiter.limit("5/minute")  # 密碼修改需要更嚴格的限制
async def update_password(
    request: Request,
    user_id: int,
    password_data: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user password
    Users can only update their own password
    """
    # Only allow updating own password
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own password",
        )

    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    await db.commit()

    return {"message": "Password updated successfully"}


# ==================== 2FA Management (Admin) ====================

@router.post("/{user_id}/reset-2fa", response_model=dict)
@limiter.limit("10/minute")
async def reset_user_2fa(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Reset 2FA for a user (Admin only)
    Use this when user loses access to authenticator.
    Sets totp_secret to "RESET" marker - user must set up 2FA on next login.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Reset 2FA with special marker (forces 2FA setup on next login)
    user.totp_enabled = False
    user.totp_secret = "RESET"  # Special marker: must set up 2FA on next login
    await db.commit()

    # Return whether the reset user is the current user (frontend needs to logout)
    is_self = user.id == current_user.id

    return {
        "message": f"2FA reset for user {user.username}",
        "is_self": is_self,
        "require_logout": True  # Always require logout after reset
    }


@router.put("/{user_id}/toggle-2fa", response_model=dict)
@limiter.limit("10/minute")
async def toggle_user_2fa(
    http_request: Request,
    user_id: int,
    request: AdminToggle2FARequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Enable or disable 2FA for a user (Admin only)
    - When disabling: Only sets totp_enabled=False, preserves totp_secret
    - When enabling: If valid totp_secret exists, directly enable; otherwise needs setup
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if request.enabled:
        # Enable 2FA - check if user has valid totp_secret
        if user.totp_secret and user.totp_secret != "RESET":
            # User has existing secret, directly enable
            user.totp_enabled = True
            message = f"2FA enabled for user {user.username}"
            needs_setup = False
        else:
            # No valid secret, needs setup
            message = f"User {user.username} needs to set up 2FA first"
            needs_setup = True
    else:
        # Disable 2FA - only set enabled to false, preserve secret
        user.totp_enabled = False
        message = f"2FA disabled for user {user.username}"
        needs_setup = False

    await db.commit()
    await db.refresh(user)

    return {
        "message": message,
        "totp_enabled": user.totp_enabled,
        "needs_setup": needs_setup if request.enabled else False
    }


@router.post("/{user_id}/reset-password", response_model=dict)
@limiter.limit("10/minute")
async def admin_reset_password(
    http_request: Request,
    user_id: int,
    request: AdminPasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Reset user password (Admin only)
    Admin can reset any user's password without knowing old password
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Reset password
    user.hashed_password = hash_password(request.new_password)
    await db.commit()

    return {"message": f"Password reset successfully for user {user.username}"}


# ==================== 2FA Enable (Admin) ====================

@router.post("/{user_id}/2fa/setup", response_model=dict)
@limiter.limit("10/minute")
async def admin_setup_2fa(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Setup 2FA for a user (Admin only)
    Generates QR code and secret for the user
    """
    from app.core.security import generate_totp_secret, get_totp_uri, generate_qrcode_base64, generate_backup_codes

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Generate new TOTP secret
    secret = generate_totp_secret()

    # Generate QR code URI
    totp_uri = get_totp_uri(secret, user.username)

    # Generate QR code image (base64)
    qr_code_base64 = generate_qrcode_base64(totp_uri)

    # Generate backup codes
    backup_codes = generate_backup_codes()

    # Save secret to user (not enabled yet)
    user.totp_secret = secret
    await db.commit()

    return {
        "secret": secret,
        "qr_code": qr_code_base64,
        "backup_codes": backup_codes,
        "message": "Scan QR code with Google Authenticator or Microsoft Authenticator"
    }


@router.post("/{user_id}/2fa/confirm", response_model=dict)
@limiter.limit("10/minute")
async def admin_confirm_2fa(
    request: Request,
    user_id: int,
    totp_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Confirm and enable 2FA for a user (Admin only)
    Verifies TOTP code to ensure setup is correct
    """
    from app.core.security import verify_totp

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not started. Call setup endpoint first.",
        )

    # Verify TOTP code
    if not verify_totp(user.totp_secret, totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code. Please try again.",
        )

    # Enable 2FA
    user.totp_enabled = True
    await db.commit()

    return {
        "success": True,
        "message": f"2FA enabled successfully for {user.username}"
    }
