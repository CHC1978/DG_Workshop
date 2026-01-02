"""Refresh Token 模型 - JWT Token 輪換機制"""
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
import secrets
import hashlib

from sqlalchemy import String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base):
    """
    Refresh Token 表 - 用於安全的 Token 輪換

    安全機制:
    - Token 以 SHA-256 雜湊儲存
    - Token Family 追蹤可偵測重播攻擊
    - 支援隨時撤銷
    """

    __tablename__ = "refresh_tokens"

    # 複合索引提升查詢效能
    __table_args__ = (
        Index('ix_refresh_tokens_user_token', 'user_id', 'token_hash'),
        Index('ix_refresh_tokens_family', 'token_family'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 使用者關聯
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Token 識別 (雜湊值)
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    # Token Family - 用於輪換追蹤 (偵測重播攻擊)
    token_family: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True
    )

    # 裝置資訊
    device_fingerprint: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    # Token 生命週期
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 時間戳記
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 關聯
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def is_valid(self) -> bool:
        """檢查 Token 是否有效"""
        return (
            not self.is_revoked
            and datetime.utcnow() < self.expires_at
        )

    def revoke(self, reason: str = "manual") -> None:
        """撤銷此 Token"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason

    def update_last_used(self) -> None:
        """更新最後使用時間"""
        self.last_used_at = datetime.utcnow()

    @classmethod
    def generate_token(cls) -> str:
        """產生安全隨機 Token"""
        return secrets.token_urlsafe(32)

    @classmethod
    def hash_token(cls, token: str) -> str:
        """雜湊 Token (SHA-256)"""
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def generate_family(cls) -> str:
        """產生唯一的 Token Family ID"""
        import uuid
        return str(uuid.uuid4())

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, valid={self.is_valid()})>"
