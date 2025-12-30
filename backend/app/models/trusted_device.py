"""Trusted device model for remember me功能"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TrustedDevice(Base):
    """Trusted device table - for 'remember this device' functionality"""

    __tablename__ = "trusted_devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # User relation
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Device fingerprint (browser + OS + IP combination)
    device_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Device info
    device_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Trust period (7 days)
    trusted_until: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="trusted_devices"
    )

    def is_valid(self) -> bool:
        """Check if trust is still valid"""
        return datetime.utcnow() < self.trusted_until

    def extend_trust(self, days: int = 7):
        """Extend trust period"""
        self.trusted_until = datetime.utcnow() + timedelta(days=days)
        self.last_used_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<TrustedDevice(id={self.id}, user_id={self.user_id}, valid={self.is_valid()})>"
