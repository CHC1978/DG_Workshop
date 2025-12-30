"""Calibration model"""
from typing import Optional
from datetime import date
from sqlalchemy import String, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Calibration(Base, TimestampMixin):
    """Calibration table"""

    __tablename__ = "calibrations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Equipment relation
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipments.id"),
        nullable=False,
        index=True
    )

    # Calibration dates
    calibration_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Provider information
    provider: Mapped[str] = mapped_column(String(200), nullable=False)
    certificate_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Cost
    cost: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    equipment: Mapped["Equipment"] = relationship(
        "Equipment",
        foreign_keys=[equipment_id]
    )

    def __repr__(self) -> str:
        return f"<Calibration(id={self.id}, equipment_id={self.equipment_id}, due='{self.next_due_date}')>"
