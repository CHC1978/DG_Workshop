"""Authentication API endpoints"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

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
    generate_refresh_token,
    hash_refresh_token,
    generate_token_family,
)
from app.core.deps import get_current_user, get_user_from_temp_token
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.used_totp_code import UsedTotpCode
from app.schemas.auth import (
    LoginStep1Request,
    LoginStep1Response,
    LoginStep2Request,
    LoginStep2Response,
    BackupCodeLoginRequest,
    Setup2FAResponse,
    Confirm2FARequest,
    Confirm2FAResponse,
    CurrentUser,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 從 main.py 獲取 limiter
from app.main import limiter


# ==================== TOTP Replay Protection Helper Functions ====================

async def _check_totp_reuse(
    db: AsyncSession,
    user_id: int,
    totp_code: str
) -> bool:
    """
    檢查 TOTP 碼是否已被使用

    Args:
        db: 資料庫 session
        user_id: 使用者 ID
        totp_code: TOTP 碼

    Returns:
        True 如果碼已被使用（應拒絕），False 如果未使用（可繼續）
    """
    code_hash = UsedTotpCode.hash_code(user_id, totp_code)

    # 查詢是否有未過期的相同碼
    result = await db.execute(
        select(UsedTotpCode).where(
            UsedTotpCode.user_id == user_id,
            UsedTotpCode.code_hash == code_hash,
            UsedTotpCode.expires_at > datetime.utcnow()
        )
    )
    existing = result.scalar_one_or_none()

    return existing is not None


async def _mark_totp_used(
    db: AsyncSession,
    user_id: int,
    totp_code: str
) -> None:
    """
    標記 TOTP 碼為已使用

    Args:
        db: 資料庫 session
        user_id: 使用者 ID
        totp_code: TOTP 碼
    """
    # 先清理過期記錄
    await _cleanup_expired_totp_codes(db, user_id)

    # 建立新記錄
    used_code = UsedTotpCode.create(user_id, totp_code)
    db.add(used_code)


async def _cleanup_expired_totp_codes(
    db: AsyncSession,
    user_id: int
) -> None:
    """
    清理使用者的過期 TOTP 碼記錄

    Args:
        db: 資料庫 session
        user_id: 使用者 ID
    """
    await db.execute(
        delete(UsedTotpCode).where(
            UsedTotpCode.user_id == user_id,
            UsedTotpCode.expires_at < datetime.utcnow()
        )
    )


async def _verify_totp_with_replay_protection(
    db: AsyncSession,
    user_id: int,
    totp_secret: str,
    totp_code: str
) -> tuple[bool, str]:
    """
    驗證 TOTP 碼並檢查重播攻擊

    Args:
        db: 資料庫 session
        user_id: 使用者 ID
        totp_secret: TOTP secret
        totp_code: TOTP 碼

    Returns:
        (is_valid, error_message) - 驗證結果和錯誤訊息
    """
    # 1. 檢查是否已使用
    if await _check_totp_reuse(db, user_id, totp_code):
        logger.warning(f"TOTP code reuse detected for user {user_id}")
        return False, "TOTP code already used. Please wait for a new code."

    # 2. 驗證 TOTP 碼
    if not verify_totp(totp_secret, totp_code):
        return False, "Invalid TOTP code"

    # 3. 標記為已使用
    await _mark_totp_used(db, user_id, totp_code)

    return True, ""


# ==================== Refresh Token Helper Functions ====================

async def _issue_refresh_token(
    response: Response,
    db: AsyncSession,
    user: User,
    request: Request,
    device_fingerprint: Optional[str] = None
) -> str:
    """
    發放新的 Refresh Token 並設定 Cookie

    Args:
        response: FastAPI Response
        db: 資料庫 session
        user: 使用者
        request: 請求物件
        device_fingerprint: 裝置指紋 (可選)

    Returns:
        refresh token 字串
    """
    # 清理過期或過多的 tokens
    await _cleanup_user_refresh_tokens(db, user.id)

    # 生成新 token
    refresh_token = generate_refresh_token()
    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        token_family=generate_token_family(),
        device_fingerprint=device_fingerprint,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token_record)

    # 設定 cookie (限制 path 到 /api/auth 提升安全性)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.SECURE_COOKIE,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/auth",
    )

    return refresh_token


async def _cleanup_user_refresh_tokens(db: AsyncSession, user_id: int) -> None:
    """
    清理使用者的 Refresh Tokens

    - 刪除過期 tokens
    - 限制活躍 token 數量 (FIFO)
    """
    # 刪除過期 tokens
    await db.execute(
        delete(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.expires_at < datetime.utcnow()
        )
    )

    # 限制活躍 token 數量
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        )
        .order_by(RefreshToken.created_at.desc())
    )
    active_tokens = result.scalars().all()

    if len(active_tokens) >= settings.MAX_REFRESH_TOKENS_PER_USER:
        # 撤銷最舊的 tokens
        for token in active_tokens[settings.MAX_REFRESH_TOKENS_PER_USER - 1:]:
            token.revoke("max_tokens_exceeded")


async def _revoke_token_family(
    db: AsyncSession,
    token_family: str,
    reason: str
) -> None:
    """撤銷整個 Token Family (用於偵測重播攻擊)"""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_family == token_family,
            RefreshToken.is_revoked == False
        )
    )
    tokens = result.scalars().all()
    for token in tokens:
        token.revoke(reason)
    await db.commit()


async def _revoke_all_user_tokens(
    db: AsyncSession,
    user_id: int,
    reason: str
) -> int:
    """撤銷使用者所有 Refresh Tokens"""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        )
    )
    tokens = result.scalars().all()
    count = 0
    for token in tokens:
        token.revoke(reason)
        count += 1
    await db.commit()
    return count


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
            logger.info(f"User {user.username} was reset, needs to set up 2FA")

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
                secure=settings.SECURE_COOKIE,
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
        logger.info(f"2FA disabled for user {user.username}, logging in directly")

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
            secure=settings.SECURE_COOKIE,  # HTTPS only in production
            samesite="lax",  # 使用 lax 在開發和生產環境都有效
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )

        # Issue refresh token
        await _issue_refresh_token(
            response=response,
            db=db,
            user=user,
            request=request,
            device_fingerprint=credentials.device_fingerprint
        )
        await db.commit()

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
            logger.info(f"Trusted device login for user {user.username}")

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
                logger.warning(f"User-Agent mismatch for trusted device. Stored: {stored_sig}, Current: {current_sig}")
                logger.warning(f"Revoking trust for device")
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
                    secure=settings.SECURE_COOKIE,  # HTTPS only in production
                    samesite="lax",
                    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    path="/",
                )

                # Issue refresh token
                await _issue_refresh_token(
                    response=response,
                    db=db,
                    user=user,
                    request=request,
                    device_fingerprint=credentials.device_fingerprint
                )
                await db.commit()

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
        secure=settings.SECURE_COOKIE,  # HTTPS only in production
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
    # Get temp_token from cookie
    temp_token = request.cookies.get("temp_token")

    if not temp_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Temporary token not found",
        )

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

    # Check if 2FA is properly set up (not RESET state)
    if not user.totp_enabled or not user.totp_secret or user.totp_secret == "RESET":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not properly enabled for this user. Please set up 2FA first.",
        )

    # 驗證 TOTP (含重播保護)
    is_valid, error_message = await _verify_totp_with_replay_protection(
        db=db,
        user_id=user.id,
        totp_secret=user.totp_secret,
        totp_code=credentials.totp_code
    )

    if not is_valid:
        logger.warning(f"TOTP verification failed for user {user.username}: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
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
        logger.info(f"Device marked as trusted for user {user.username}")

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
        secure=settings.SECURE_COOKIE,  # HTTPS only in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    # Issue refresh token
    await _issue_refresh_token(
        response=response,
        db=db,
        user=user,
        request=request,
        device_fingerprint=credentials.device_fingerprint
    )
    await db.commit()

    # Clear temp_token cookie
    response.delete_cookie(key="temp_token", path="/")

    return LoginStep2Response(
        access_token=None,  # Don't return token in response body
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role.value,
    )


@router.post("/login/backup-code", response_model=LoginStep2Response)
@limiter.limit("3/minute")  # 更嚴格的速率限制，因為備用碼更敏感
async def login_with_backup_code(
    request: Request,
    response: Response,
    credentials: BackupCodeLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login using backup code instead of TOTP
    This is for emergency access when authenticator app is unavailable
    Each backup code can only be used once
    """
    from app.models.backup_code import BackupCode
    from app.core.security import verify_password

    # Get temp_token from cookie
    temp_token = request.cookies.get("temp_token")

    if not temp_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Temporary token not found",
        )

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

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Get all unused backup codes for this user
    result = await db.execute(
        select(BackupCode).where(
            BackupCode.user_id == user.id,
            BackupCode.is_used == False
        )
    )
    backup_codes = result.scalars().all()

    # Try to verify the provided backup code against stored hashes
    valid_code = None
    for stored_code in backup_codes:
        if verify_password(credentials.backup_code.upper(), stored_code.code_hash):
            valid_code = stored_code
            break

    if not valid_code:
        logger.warning(f"Invalid backup code attempt for user {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or already used backup code",
        )

    # Mark the backup code as used
    valid_code.mark_as_used()
    await db.commit()

    logger.info(f"User {user.username} logged in using backup code")

    # Generate access token
    access_token = create_access_token({
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value,
    })

    # Set httpOnly cookie for access token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.SECURE_COOKIE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    # Issue refresh token
    await _issue_refresh_token(
        response=response,
        db=db,
        user=user,
        request=request,
        device_fingerprint=None  # 備用碼登入不綁定裝置指紋
    )
    await db.commit()

    # Clear temp_token cookie
    response.delete_cookie(key="temp_token", path="/")

    # Get remaining backup codes count
    remaining = len([c for c in backup_codes if c.id != valid_code.id])
    if remaining <= 2:
        logger.warning(f"User {user.username} has only {remaining} backup codes remaining")

    return LoginStep2Response(
        access_token=None,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role.value,
    )


# ==================== 2FA Setup Endpoints ====================

@router.post("/2fa/setup", response_model=Setup2FAResponse)
@limiter.limit("5/minute")
async def setup_2fa(
    request: Request,
    current_user: User = Depends(get_user_from_temp_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Setup 2FA for current user
    Requires temporary token from login step 1
    Returns QR code and backup codes
    """
    from app.models.backup_code import BackupCode
    from app.core.security import hash_password

    # Generate TOTP secret
    secret = generate_totp_secret()

    # Generate QR code URI
    totp_uri = get_totp_uri(secret, current_user.username)

    # Generate QR code image (base64)
    qr_code_base64 = generate_qrcode_base64(totp_uri)

    # Generate backup codes
    backup_codes = generate_backup_codes()

    # Delete existing backup codes for this user
    existing_codes = await db.execute(
        select(BackupCode).where(BackupCode.user_id == current_user.id)
    )
    for code in existing_codes.scalars().all():
        await db.delete(code)

    # Store hashed backup codes in database
    for code in backup_codes:
        hashed_code = hash_password(code)  # Use bcrypt hash
        backup_code = BackupCode(
            user_id=current_user.id,
            code_hash=hashed_code
        )
        db.add(backup_code)

    # Save secret to user (not enabled yet)
    current_user.totp_secret = secret
    await db.commit()

    logger.info(f"2FA setup initiated for user {current_user.username}, {len(backup_codes)} backup codes generated")

    return Setup2FAResponse(
        secret=secret,
        qr_code=qr_code_base64,
        backup_codes=backup_codes,
        message="Scan QR code with Google Authenticator or Microsoft Authenticator"
    )


@router.post("/2fa/confirm", response_model=Confirm2FAResponse)
@limiter.limit("5/minute")
async def confirm_2fa(
    http_request: Request,
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

    # Verify TOTP code (含重播保護)
    is_valid, error_message = await _verify_totp_with_replay_protection(
        db=db,
        user_id=current_user.id,
        totp_secret=current_user.totp_secret,
        totp_code=request.totp_code
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "Invalid TOTP code. Please try again.",
        )

    # Enable 2FA
    current_user.totp_enabled = True
    await db.commit()

    return Confirm2FAResponse(
        success=True,
        message="2FA enabled successfully"
    )


@router.post("/2fa/disable", response_model=Confirm2FAResponse)
@limiter.limit("5/minute")
async def disable_2fa(
    http_request: Request,
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

    # Verify TOTP code (含重播保護)
    is_valid, error_message = await _verify_totp_with_replay_protection(
        db=db,
        user_id=current_user.id,
        totp_secret=current_user.totp_secret,
        totp_code=request.totp_code
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "Invalid TOTP code",
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
async def logout(
    request: Request,
    response: Response,
    logout_all: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user by clearing authentication cookies and revoking refresh tokens

    Args:
        logout_all: If True, revoke all refresh tokens and trusted devices for this user
    """
    from app.models.trusted_device import TrustedDevice

    user_id = None
    revoked_tokens = 0

    # Get user_id from access_token or refresh_token
    token = request.cookies.get("access_token")
    if token:
        payload = decode_token(token)
        if payload and payload.get("sub"):
            try:
                user_id = int(payload.get("sub"))
            except (ValueError, TypeError):
                pass

    # Revoke current refresh token
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        token_hash = hash_refresh_token(refresh_token)
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()

        if stored_token:
            if user_id is None:
                user_id = stored_token.user_id

            if logout_all:
                # 撤銷使用者所有 refresh tokens
                revoked_tokens = await _revoke_all_user_tokens(db, stored_token.user_id, "logout_all")
            else:
                # 只撤銷當前 token family
                await _revoke_token_family(db, stored_token.token_family, "logout")
                revoked_tokens = 1

    # If logout_all is requested, also clear all trusted devices
    if logout_all and user_id:
        result = await db.execute(
            select(TrustedDevice).where(TrustedDevice.user_id == user_id)
        )
        devices = result.scalars().all()
        for device in devices:
            await db.delete(device)
        await db.commit()
        logger.info(f"Revoked {len(devices)} trusted devices and {revoked_tokens} refresh tokens for user {user_id}")

    # Clear authentication cookies
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="temp_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/auth")

    return {
        "message": "Logout successful",
        "all_devices_revoked": logout_all
    }


# ==================== Refresh Token Endpoints ====================

@router.post("/refresh")
@limiter.limit("30/minute")  # 每分鐘最多 30 次刷新
async def refresh_access_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    使用 Refresh Token 換取新的 Access Token

    Token 輪換: 每次刷新會生成新的 refresh_token
    """
    # 1. 從 cookie 取得 refresh_token
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    # 2. 計算 token hash 並查詢
    token_hash = hash_refresh_token(refresh_token)
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .options(selectinload(RefreshToken.user))
    )
    stored_token = result.scalar_one_or_none()

    # 3. 驗證 token 存在
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # 4. 檢查是否已撤銷 (可能是重播攻擊)
    if stored_token.is_revoked:
        # 偵測到重播攻擊：撤銷整個 token family
        await _revoke_token_family(db, stored_token.token_family, "reuse_detected")
        logger.warning(f"Refresh token reuse detected for user {stored_token.user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please login again."
        )

    # 5. 檢查是否過期
    if not stored_token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    # 6. 檢查用戶狀態
    user = stored_token.user
    if not user or not user.is_active:
        stored_token.revoke("user_inactive")
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # 7. Token Rotation: 撤銷舊 token，發放新 token
    stored_token.revoke("rotated")

    # 生成新的 refresh token (保持相同 family)
    new_refresh_token = generate_refresh_token()
    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh_token),
        token_family=stored_token.token_family,  # 保持相同 family
        device_fingerprint=stored_token.device_fingerprint,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_token_record)

    # 8. 生成新的 access token
    access_token = create_access_token({
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value,
    })

    await db.commit()

    # 9. 設定 cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.SECURE_COOKIE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.SECURE_COOKIE,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/auth",
    )

    logger.info(f"Token refreshed for user {user.username}")

    return {
        "message": "Token refreshed successfully",
        "token_type": "bearer"
    }


@router.get("/sessions")
async def get_active_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取得當前使用者的所有活躍 sessions (refresh tokens)
    """
    # 取得當前的 refresh token (用於標記 is_current)
    current_refresh_token = request.cookies.get("refresh_token")
    current_token_hash = hash_refresh_token(current_refresh_token) if current_refresh_token else None

    # 查詢所有活躍的 refresh tokens
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
        .order_by(RefreshToken.last_used_at.desc().nullsfirst(), RefreshToken.created_at.desc())
    )
    tokens = result.scalars().all()

    sessions = []
    for token in tokens:
        sessions.append({
            "id": token.id,
            "device_fingerprint": token.device_fingerprint,
            "user_agent": token.user_agent,
            "ip_address": token.ip_address,
            "created_at": token.created_at.isoformat() if token.created_at else None,
            "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
            "is_current": token.token_hash == current_token_hash
        })

    return {
        "sessions": sessions,
        "total": len(sessions)
    }


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    撤銷指定的 session (refresh token)
    """
    # 查詢 token
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.id == session_id,
            RefreshToken.user_id == current_user.id
        )
    )
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already revoked"
        )

    # 撤銷整個 token family
    await _revoke_token_family(db, token.token_family, "user_revoked")

    return {
        "message": "Session revoked successfully",
        "session_id": session_id
    }
