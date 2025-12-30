"""Log attachment model"""
import enum
from typing import Optional
from sqlalchemy import String, Integer, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class AttachmentType(str, enum.Enum):
    """Attachment type"""
    CALIBRATION_REPORT = "calibration_report"
    DAMAGE_PHOTO = "damage_photo"
    REPAIR_DOCUMENT = "repair_document"
    MAINTENANCE_RECORD = "maintenance_record"
    RENTAL_CONTRACT = "rental_contract"
    OTHER = "other"


class LogAttachment(Base, TimestampMixin):
    """Log attachment table"""

    __tablename__ = "log_attachments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Log relation
    equipment_log_id: Mapped[int] = mapped_column(
        ForeignKey("equipment_logs.id"),
        nullable=False,
        index=True
    )

    # File information
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[AttachmentType] = mapped_column(
        SQLEnum(AttachmentType),
        nullable=False
    )
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Upload tracking
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    # Relationships
    equipment_log: Mapped["EquipmentLog"] = relationship(
        "EquipmentLog",
        back_populates="attachments"
    )
    uploader: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[uploaded_by]
    )

    def __repr__(self) -> str:
        return f"<LogAttachment(id={self.id}, log_id={self.equipment_log_id}, file='{self.file_name}')>"
