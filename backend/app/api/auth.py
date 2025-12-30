"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    create_temp_token,
    decode_token,
    generate_totp_secret,
    get_totp_uri,
    generate_qrcode_base64,
    verify_totp,
    generate_backup_codes,
)
from app.core.deps import get_current_user, get_user_from_temp_token
from app.models.user import User
from app.schemas.auth import (
    LoginStep1Request,
    LoginStep1Response,
    LoginStep2Request,
    LoginStep2Response,
    Setup2FAResponse,
    Confirm2FARequest,
    Confirm2FAResponse,
    CurrentUser,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==================== Login Endpoints ====================

@router.post("/login/step1", response_model=LoginStep1Response)
async def login_step1(
    credentials: LoginStep1Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 1: Verify username and password
    Returns a temporary token for Step 2
    """
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Generate temporary token (short-lived)
    temp_token = create_temp_token({
        "sub": str(user.id),  # JWT spec requires sub to be a string
        "username": user.username,
        "type": "temp"
    })

    return LoginStep1Response(
        temp_token=temp_token,
        totp_required=user.totp_enabled,
        message="2FA required" if user.totp_enabled else "2FA setup required"
    )


@router.post("/login/step2", response_model=LoginStep2Response)
async def login_step2(
    credentials: LoginStep2Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Verify TOTP code
    Returns access token
    """
    # Decode temporary token
    payload = decode_token(credentials.temp_token)
    if not payload or payload.get("type") != "temp":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired temporary token",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Verify TOTP code
    if not user.totp_enabled or not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this user. Please set up 2FA first.",
        )

    if not verify_totp(user.totp_secret, credentials.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    # Generate access token
    access_token = create_access_token({
        "sub": str(user.id),  # JWT spec requires sub to be a string
        "username": user.username,
        "role": user.role.value,
    })

    return LoginStep2Response(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role.value,
    )


# ==================== 2FA Setup Endpoints ====================

@router.post("/2fa/setup", response_model=Setup2FAResponse)
async def setup_2fa(
    current_user: User = Depends(get_user_from_temp_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Setup 2FA for current user
    Requires temporary token from login step 1
    Returns QR code and backup codes
    """
    # Generate TOTP secret
    secret = generate_totp_secret()

    # Generate QR code URI
    totp_uri = get_totp_uri(secret, current_user.username)

    # Generate QR code image (base64)
    qr_code_base64 = generate_qrcode_base64(totp_uri)

    # Generate backup codes
    backup_codes = generate_backup_codes()

    # Save secret to user (not enabled yet)
    current_user.totp_secret = secret
    await db.commit()

    return Setup2FAResponse(
        secret=secret,
        qr_code=qr_code_base64,
        backup_codes=backup_codes,
        message="Scan QR code with Google Authenticator or Microsoft Authenticator"
    )


@router.post("/2fa/confirm", response_model=Confirm2FAResponse)
async def confirm_2fa(
    request: Confirm2FARequest,
    current_user: User = Depends(get_user_from_temp_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm and enable 2FA
    Requires temporary token from login step 1
    Verify TOTP code to ensure setup is correct
    """
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not started. Call /auth/2fa/setup first.",
        )

    # Verify TOTP code
    if not verify_totp(current_user.totp_secret, request.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code. Please try again.",
        )

    # Enable 2FA
    current_user.totp_enabled = True
    await db.commit()

    return Confirm2FAResponse(
        success=True,
        message="2FA enabled successfully"
    )


@router.post("/2fa/disable", response_model=Confirm2FAResponse)
async def disable_2fa(
    request: Confirm2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable 2FA for current user
    Requires TOTP code verification
    """
    if not current_user.totp_enabled or not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled",
        )

    # Verify TOTP code
    if not verify_totp(current_user.totp_secret, request.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    # Disable 2FA
    current_user.totp_enabled = False
    current_user.totp_secret = None
    await db.commit()

    return Confirm2FAResponse(
        success=True,
        message="2FA disabled successfully"
    )


# ==================== Current User Endpoint ====================

@router.get("/me", response_model=CurrentUser)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return CurrentUser(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        totp_enabled=current_user.totp_enabled,
        is_active=current_user.is_active,
    )
