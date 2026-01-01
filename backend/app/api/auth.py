"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
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

# 從 main.py 獲取 limiter
from app.main import limiter


# ==================== Login Endpoints ====================

@router.post("/login/step1", response_model=LoginStep1Response)
@limiter.limit("5/minute")  # 每分鐘最多 5 次嘗試
async def login_step1(
    request: Request,
    response: Response,
    credentials: LoginStep1Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 1: Verify username and password
    Check if device is trusted (skip 2FA for 7 days)
    Returns access token if trusted, otherwise temp token for Step 2
    """
    from app.models.trusted_device import TrustedDevice
    from datetime import datetime

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

    # If 2FA is not enabled
    if not user.totp_enabled:
        # Check if user was reset (totp_secret == "RESET") - must set up 2FA
        if user.totp_secret == "RESET":
            # User was reset by admin - must set up 2FA before login
            print(f"[INFO] User {user.username} was reset, needs to set up 2FA")

            # Generate temporary token for 2FA setup
            temp_token = create_temp_token({
                "sub": str(user.id),
                "username": user.username,
                "type": "temp"
            })

            # Set httpOnly cookie for temp token
            response.set_cookie(
                key="temp_token",
                value=temp_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="lax",
                max_age=settings.TEMP_TOKEN_EXPIRE_MINUTES * 60,
                path="/",
            )

            return LoginStep1Response(
                temp_token=None,
                totp_required=False,
                needs_2fa_setup=True,
                trusted_device=False,
                message="2FA setup required"
            )

        # 2FA is disabled (totp_secret == None) - login directly without 2FA
        print(f"[INFO] 2FA disabled for user {user.username}, logging in directly")

        # Generate access token directly
        access_token = create_access_token({
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
        })

        # Set httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,  # HTTPS only in production
            samesite="lax",  # 使用 lax 在開發和生產環境都有效
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )

        return LoginStep1Response(
            access_token=None,  # Don't return token in response body
            totp_required=False,
            needs_2fa_setup=False,
            trusted_device=False,
            message="Login successful"
        )

    # Check if this is a trusted device (only if 2FA is enabled)
    if credentials.device_fingerprint:
        result = await db.execute(
            select(TrustedDevice).where(
                TrustedDevice.user_id == user.id,
                TrustedDevice.device_fingerprint == credentials.device_fingerprint
            )
        )
        trusted_device = result.scalar_one_or_none()

        if trusted_device and trusted_device.is_valid():
            # Device is trusted and still valid, skip 2FA
            print(f"[INFO] Trusted device login for user {user.username}")

            # 驗證 User-Agent 一致性 (允許瀏覽器版本更新)
            current_user_agent = request.headers.get("user-agent", "")
            stored_user_agent = trusted_device.user_agent or ""

            # 簡單驗證：檢查主要瀏覽器和 OS 是否相同
            # 允許版本號變化 (例如 Chrome/120 -> Chrome/121)
            def extract_browser_os(ua: str) -> tuple:
                """提取瀏覽器和作業系統主要標識"""
                browser = ""
                if "Chrome" in ua: browser = "Chrome"
                elif "Firefox" in ua: browser = "Firefox"
                elif "Safari" in ua: browser = "Safari"
                elif "Edge" in ua: browser = "Edge"

                os_name = ""
                if "Windows" in ua: os_name = "Windows"
                elif "Mac" in ua: os_name = "Mac"
                elif "Linux" in ua: os_name = "Linux"
                elif "Android" in ua: os_name = "Android"
                elif "iOS" in ua: os_name = "iOS"

                return (browser, os_name)

            current_sig = extract_browser_os(current_user_agent)
            stored_sig = extract_browser_os(stored_user_agent)

            if current_sig != stored_sig and stored_user_agent:
                # User-Agent 變化可疑，撤銷信任
                print(f"[WARNING] User-Agent mismatch for trusted device. "
                      f"Stored: {stored_sig}, Current: {current_sig}")
                print(f"[WARNING] Revoking trust for device {credentials.device_fingerprint}")
                # 不使用此信任設備，要求 2FA (繼續執行到下面的 temp_token 邏輯)
            else:
                # User-Agent 一致，延長信任期
                trusted_device.extend_trust(days=7)
                # 更新 User-Agent 和 IP (版本更新)
                trusted_device.user_agent = current_user_agent
                trusted_device.ip_address = request.client.host if request.client else None
                await db.commit()

                # Generate access token directly
                access_token = create_access_token({
                    "sub": str(user.id),
                    "username": user.username,
                    "role": user.role.value,
                })

                # Set httpOnly cookie
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=not settings.DEBUG,  # HTTPS only in production
                    samesite="lax",
                    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    path="/",
                )

                return LoginStep1Response(
                    access_token=None,  # Don't return token in response body
                    totp_required=False,
                    trusted_device=True,
                    message="Login successful (trusted device)"
                )

    # 2FA is enabled and not a trusted device - require TOTP
    # Generate temporary token (short-lived)
    temp_token = create_temp_token({
        "sub": str(user.id),
        "username": user.username,
        "type": "temp"
    })

    # Set httpOnly cookie for temp token
    response.set_cookie(
        key="temp_token",
        value=temp_token,
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite="lax",
        max_age=settings.TEMP_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return LoginStep1Response(
        temp_token=None,  # Don't return token in response body
        totp_required=True,
        trusted_device=False,
        message="2FA required"
    )


@router.post("/login/step2", response_model=LoginStep2Response)
@limiter.limit("10/minute")  # 每分鐘最多 10 次嘗試 (較 step1 寬鬆，因為已有 temp token)
async def login_step2(
    request: Request,
    response: Response,
    credentials: LoginStep2Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Verify TOTP code
    Returns access token
    """
    try:
        print(f"[DEBUG] login_step2 called")
        print(f"[DEBUG] Cookies: {request.cookies}")
        print(f"[DEBUG] Credentials: {credentials}")

        # Get temp_token from cookie
        temp_token = request.cookies.get("temp_token")
        print(f"[DEBUG] temp_token from cookie: {temp_token[:20] if temp_token else 'None'}...")

        if not temp_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Temporary token not found",
            )
    except Exception as e:
        print(f"[ERROR] Exception in login_step2: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

    # Decode temporary token
    payload = decode_token(temp_token)
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
    print(f"[DEBUG] user.totp_enabled: {user.totp_enabled}")
    print(f"[DEBUG] user.totp_secret exists: {bool(user.totp_secret)}")
    print(f"[DEBUG] user.totp_secret value: {user.totp_secret[:10] if user.totp_secret and len(user.totp_secret) > 10 else user.totp_secret}")
    print(f"[DEBUG] totp_code from request: {credentials.totp_code}")

    # Check if 2FA is properly set up (not RESET state)
    if not user.totp_enabled or not user.totp_secret or user.totp_secret == "RESET":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not properly enabled for this user. Please set up 2FA first.",
        )

    # 驗證 TOTP
    is_valid = verify_totp(user.totp_secret, credentials.totp_code)
    print(f"[DEBUG] TOTP verification result: {is_valid}")

    if not is_valid:
        print(f"[ERROR] TOTP verification failed for user {user.username}")
        print(f"[ERROR] Expected TOTP secret length: {len(user.totp_secret) if user.totp_secret else 0}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )

    # Save as trusted device if requested
    if credentials.remember_device and credentials.device_fingerprint:
        from app.models.trusted_device import TrustedDevice
        from datetime import datetime, timedelta

        # Check if device already exists
        result = await db.execute(
            select(TrustedDevice).where(
                TrustedDevice.user_id == user.id,
                TrustedDevice.device_fingerprint == credentials.device_fingerprint
            )
        )
        existing_device = result.scalar_one_or_none()

        if existing_device:
            # Update existing device
            existing_device.extend_trust(days=7)
            # 更新 User-Agent 和 IP
            existing_device.user_agent = request.headers.get("user-agent")
            existing_device.ip_address = request.client.host if request.client else None
        else:
            # Create new trusted device
            new_device = TrustedDevice(
                user_id=user.id,
                device_fingerprint=credentials.device_fingerprint,
                device_name=credentials.device_name or "Unknown Device",
                user_agent=request.headers.get("user-agent"),
                ip_address=request.client.host if request.client else None,
                trusted_until=datetime.utcnow() + timedelta(days=7),
                last_used_at=datetime.utcnow(),
            )
            db.add(new_device)

        await db.commit()
        print(f"[INFO] Device marked as trusted for user {user.username}")

    # Generate access token
    access_token = create_access_token({
        "sub": str(user.id),  # JWT spec requires sub to be a string
        "username": user.username,
        "role": user.role.value,
    })

    # Set httpOnly cookie for access token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    # Clear temp_token cookie
    response.delete_cookie(key="temp_token", path="/")

    return LoginStep2Response(
        access_token=None,  # Don't return token in response body
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


# ==================== Logout Endpoint ====================

@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing authentication cookies
    """
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="temp_token", path="/")
    return {"message": "Logout successful"}
