"""Used TOTP Code 模型 - TOTP 重播保護"""
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
import hashlib

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User

# TOTP 碼保留時間 (秒)
# TOTP 有效期 30 秒，保留 60 秒避免時鐘偏差
TOTP_CODE_RETENTION_SECONDS = 60


class UsedTotpCode(Base):
    """
    已使用的 TOTP 碼記錄

    用於防止 TOTP 重播攻擊 - 同一個驗證碼不能在有效期內重複使用
    """

    __tablename__ = "used_totp_codes"

    # 複合索引提升查詢效能
    __table_args__ = (
        Index('ix_used_totp_codes_user_hash', 'user_id', 'code_hash'),
        Index('ix_used_totp_codes_expires', 'expires_at'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 使用者關聯
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # TOTP 碼雜湊 (SHA-256 of user_id + code)
    code_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True
    )

    # 時間戳記
    used_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # 過期時間
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    # 關聯
    user: Mapped["User"] = relationship("User", back_populates="used_totp_codes")

    @classmethod
    def hash_code(cls, user_id: int, totp_code: str) -> str:
        """
        產生 TOTP 碼雜湊

        Args:
            user_id: 使用者 ID
            totp_code: TOTP 碼

        Returns:
            SHA-256 雜湊值
        """
        data = f"{user_id}:{totp_code}"
        return hashlib.sha256(data.encode()).hexdigest()

    @classmethod
    def create(cls, user_id: int, totp_code: str) -> "UsedTotpCode":
        """
        建立新的已使用 TOTP 碼記錄

        Args:
            user_id: 使用者 ID
            totp_code: TOTP 碼

        Returns:
            UsedTotpCode 實例
        """
        now = datetime.utcnow()
        return cls(
            user_id=user_id,
            code_hash=cls.hash_code(user_id, totp_code),
            used_at=now,
            expires_at=now + timedelta(seconds=TOTP_CODE_RETENTION_SECONDS)
        )

    def is_expired(self) -> bool:
        """檢查記錄是否已過期"""
        return datetime.utcnow() > self.expires_at

    def __repr__(self) -> str:
        return f"<UsedTotpCode(id={self.id}, user_id={self.user_id}, expired={self.is_expired()})>"
