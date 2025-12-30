"""Equipment log model"""
import enum
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, Float, ForeignKey, Enum as SQLEnum, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class EquipmentLogType(str, enum.Enum):
    """Equipment log type"""
    STATUS_CHANGE = "status_change"
    LOCATION_CHANGE = "location_change"
    RENTAL_START = "rental_start"
    RENTAL_END = "rental_end"
    CALIBRATION = "calibration"
    MAINTENANCE = "maintenance"
    NOTE = "note"
    CREATED = "created"
    UPDATED = "updated"


class EquipmentLog(Base, TimestampMixin):
    """Equipment log table - records all equipment changes"""

    __tablename__ = "equipment_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipments.id"),
        nullable=False,
        index=True,
        comment="設備 ID（可以是主設備或子設備，透過 is_sub_equipment 區分）"
    )
    is_sub_equipment: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="True 表示此 log 屬於子設備，equipment_id 指向 sub_equipments 表"
    )
    log_type: Mapped[EquipmentLogType] = mapped_column(
        SQLEnum(EquipmentLogType),
        nullable=False,
        index=True
    )

    # Change tracking
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location tracking (optional)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # User tracking
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    # Edit tracking
    edited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Last edited time"
    )
    edited_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        comment="User who last edited this log"
    )
    edit_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times this log has been edited"
    )
    original_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Original description before first edit"
    )
    original_latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Original latitude before first edit"
    )
    original_longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Original longitude before first edit"
    )

    # Relationships
    equipment: Mapped["Equipment"] = relationship(
        "Equipment",
        back_populates="logs"
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        viewonly=True,
        overlaps="editor"
    )
    editor: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[edited_by],
        viewonly=True,
        overlaps="creator"
    )
    attachments: Mapped[list["LogAttachment"]] = relationship(
        "LogAttachment",
        back_populates="equipment_log",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<EquipmentLog(id={self.id}, equipment_id={self.equipment_id}, type='{self.log_type.value}')>"
