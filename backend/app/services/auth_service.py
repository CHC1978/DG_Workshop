"""
Auth Service - Business logic for authentication and token management
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List

from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    verify_totp,
    generate_refresh_token,
    hash_refresh_token,
    generate_token_family,
)
from app.core.csrf import set_csrf_cookie, clear_csrf_cookie
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.used_totp_code import UsedTotpCode

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== TOTP Replay Protection ====================

    async def check_totp_reuse(
        self,
        user_id: int,
        totp_code: str
    ) -> bool:
        """
        Check if TOTP code has already been used.

        Args:
            user_id: User ID
            totp_code: TOTP code

        Returns:
            True if code was already used (should reject), False if not used
        """
        code_hash = UsedTotpCode.hash_code(user_id, totp_code)

        result = await self.db.execute(
            select(UsedTotpCode).where(
                UsedTotpCode.user_id == user_id,
                UsedTotpCode.code_hash == code_hash,
                UsedTotpCode.expires_at > datetime.utcnow()
            )
        )
        existing = result.scalar_one_or_none()

        return existing is not None

    async def mark_totp_used(
        self,
        user_id: int,
        totp_code: str
    ) -> None:
        """
        Mark TOTP code as used.

        Args:
            user_id: User ID
            totp_code: TOTP code
        """
        # Clean up expired records first
        await self.cleanup_expired_totp_codes(user_id)

        # Create new record
        used_code = UsedTotpCode.create(user_id, totp_code)
        self.db.add(used_code)

    async def cleanup_expired_totp_codes(
        self,
        user_id: int
    ) -> None:
        """
        Clean up expired TOTP code records for a user.

        Args:
            user_id: User ID
        """
        await self.db.execute(
            delete(UsedTotpCode).where(
                UsedTotpCode.user_id == user_id,
                UsedTotpCode.expires_at < datetime.utcnow()
            )
        )

    async def verify_totp_with_replay_protection(
        self,
        user_id: int,
        totp_secret: str,
        totp_code: str
    ) -> Tuple[bool, str]:
        """
        Verify TOTP code with replay attack protection.

        Args:
            user_id: User ID
            totp_secret: TOTP secret
            totp_code: TOTP code

        Returns:
            (is_valid, error_message) - Validation result and error message
        """
        # 1. Check if already used
        if await self.check_totp_reuse(user_id, totp_code):
            logger.warning(f"TOTP code reuse detected for user {user_id}")
            return False, "TOTP code already used. Please wait for a new code."

        # 2. Verify TOTP code
        if not verify_totp(totp_secret, totp_code):
            return False, "Invalid TOTP code"

        # 3. Mark as used
        await self.mark_totp_used(user_id, totp_code)

        return True, ""

    # ==================== Refresh Token Management ====================

    async def issue_refresh_token(
        self,
        response: Response,
        user: User,
        request: Request,
        device_fingerprint: Optional[str] = None
    ) -> str:
        """
        Issue new Refresh Token and set cookie.

        Args:
            response: FastAPI Response
            user: User object
            request: Request object
            device_fingerprint: Device fingerprint (optional)

        Returns:
            refresh token string
        """
        # Clean up expired or excess tokens
        await self.cleanup_user_refresh_tokens(user.id)

        # Generate new token
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
        self.db.add(token_record)

        # Set cookie (restrict path to /api/auth for security)
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

    async def cleanup_user_refresh_tokens(self, user_id: int) -> None:
        """
        Clean up user's Refresh Tokens.

        - Delete expired tokens
        - Limit active token count (FIFO)
        """
        # Delete expired tokens
        await self.db.execute(
            delete(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.expires_at < datetime.utcnow()
            )
        )

        # Limit active token count
        result = await self.db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
            .order_by(RefreshToken.created_at.desc())
        )
        active_tokens = result.scalars().all()

        if len(active_tokens) >= settings.MAX_REFRESH_TOKENS_PER_USER:
            # Revoke oldest tokens
            for token in active_tokens[settings.MAX_REFRESH_TOKENS_PER_USER - 1:]:
                token.revoke("max_tokens_exceeded")

    async def revoke_token_family(
        self,
        token_family: str,
        reason: str
    ) -> None:
        """Revoke entire Token Family (for replay attack detection)"""
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_family == token_family,
                RefreshToken.is_revoked == False
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.revoke(reason)
        await self.db.commit()

    async def revoke_all_user_tokens(
        self,
        user_id: int,
        reason: str
    ) -> int:
        """Revoke all user's Refresh Tokens"""
        result = await self.db.execute(
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
        await self.db.commit()
        return count

    async def find_refresh_token(
        self,
        token_hash: str
    ) -> Optional[RefreshToken]:
        """Find refresh token by hash"""
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def get_active_sessions(
        self,
        user_id: int
    ) -> List[RefreshToken]:
        """Get all active sessions (non-revoked refresh tokens) for a user"""
        result = await self.db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
            .order_by(RefreshToken.last_used_at.desc().nulls_last())
        )
        return list(result.scalars().all())

    async def revoke_session(
        self,
        session_id: int,
        user_id: int,
        reason: str = "user_logout"
    ) -> bool:
        """
        Revoke a specific session.

        Returns:
            True if session was found and revoked, False otherwise
        """
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.id == session_id,
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        )
        token = result.scalar_one_or_none()

        if not token:
            return False

        token.revoke(reason)
        return True

    # ==================== User Authentication ====================

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def verify_user_password(self, user: User, password: str) -> bool:
        """Verify user password"""
        return verify_password(password, user.hashed_password)

    def create_access_token_for_user(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token for user"""
        return create_access_token(
            subject=str(user.id),
            expires_delta=expires_delta,
        )

    # ==================== Logout ====================

    async def logout_user(
        self,
        response: Response,
        user_id: int,
        refresh_token: Optional[str] = None,
        logout_all: bool = False
    ) -> int:
        """
        Logout user by revoking tokens.

        Args:
            response: FastAPI Response
            user_id: User ID
            refresh_token: Current refresh token (optional)
            logout_all: If True, revoke all tokens for user

        Returns:
            Number of tokens revoked
        """
        revoked_count = 0

        if logout_all:
            revoked_count = await self.revoke_all_user_tokens(
                user_id,
                reason="user_logout_all"
            )
        elif refresh_token:
            # Revoke just this token
            token_hash = hash_refresh_token(refresh_token)
            token_record = await self.find_refresh_token(token_hash)
            if token_record and not token_record.is_revoked:
                token_record.revoke("user_logout")
                revoked_count = 1

        # Clear cookies
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/api/auth")
        clear_csrf_cookie(response)

        return revoked_count
