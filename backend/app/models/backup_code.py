"""Backup code model for 2FA recovery"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BackupCode(Base):
    """Backup codes for 2FA recovery - stored as hashed values"""

    __tablename__ = "backup_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # User relation
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Hashed backup code (using bcrypt)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Usage tracking
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="backup_codes"
    )

    def mark_as_used(self):
        """Mark this backup code as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<BackupCode(id={self.id}, user_id={self.user_id}, used={self.is_used})>"
