"""Maintenance model"""
from typing import Optional
from datetime import date
from sqlalchemy import String, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Maintenance(Base, TimestampMixin):
    """Maintenance table - Equipment maintenance records"""

    __tablename__ = "maintenances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Equipment relation
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipments.id"),
        nullable=False,
        index=True
    )

    # Maintenance dates
    maintenance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Service provider information
    provider: Mapped[str] = mapped_column(String(200), nullable=False)
    service_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "Preventive", "Repair", "Overhaul"

    # Cost
    cost: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Report file
    report_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    equipment: Mapped["Equipment"] = relationship(
        "Equipment",
        foreign_keys=[equipment_id]
    )

    def __repr__(self) -> str:
        return f"<Maintenance(id={self.id}, equipment_id={self.equipment_id}, due='{self.next_due_date}')>"
