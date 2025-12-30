"""Rental model"""
import enum
from typing import Optional
from datetime import date
from sqlalchemy import String, Numeric, Date, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class RentalStatus(str, enum.Enum):
    """Rental status"""
    DRAFT = "draft"            # 草稿/報價中
    CONFIRMED = "confirmed"    # 已確認
    ACTIVE = "active"          # 租賃中
    OVERDUE = "overdue"        # 逾期未還
    RETURNED = "returned"      # 已歸還
    CANCELLED = "cancelled"    # 已取消


class Rental(Base, TimestampMixin):
    """Rental table"""

    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Rental number (auto-generated)
    rental_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    # Relations
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipments.id"),
        nullable=False,
        index=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    # Rental period
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Financial
    daily_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    deposit_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    total_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)

    # Status
    status: Mapped[RentalStatus] = mapped_column(
        SQLEnum(RentalStatus),
        default=RentalStatus.DRAFT,
        nullable=False,
        index=True
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    return_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    equipment: Mapped["Equipment"] = relationship(
        "Equipment",
        foreign_keys=[equipment_id]
    )
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="rentals",
        foreign_keys=[customer_id]
    )

    def __repr__(self) -> str:
        return f"<Rental(id={self.id}, number='{self.rental_number}', status='{self.status.value}')>"
