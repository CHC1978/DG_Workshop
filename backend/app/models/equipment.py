"""設備模型"""
import enum
from typing import Optional
from datetime import date
from sqlalchemy import String, Numeric, Date, Text, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class EquipmentCategory(str, enum.Enum):
    """設備類別"""
    MBES = "mbes"              # 多音束測深儀 (Multibeam Echosounder)
    GNSS = "gnss"              # 衛星定位系統 (GNSS Receiver)
    SVP = "svp"                # 聲速剖面儀 (Sound Velocity Profiler)
    SBP = "sbp"                # 淺層剖面儀 (Sub-bottom Profiler)
    USBL = "usbl"              # 水下定位系統 (Ultra-Short Baseline)
    ROV = "rov"                # 水下無人載具 (Remotely Operated Vehicle)
    INS = "ins"                # 慣性導航系統 (Inertial Navigation System)
    MAG = "magnetometer"       # 磁力儀 (Magnetometer)
    OTHER = "other"            # 其他


class EquipmentStatus(str, enum.Enum):
    """設備狀態"""
    ORDERING = "ordering"      # 採購中
    IN_STOCK = "in_stock"      # 庫存中
    DEPLOYED = "deployed"      # 自用部署中
    RENTED = "rented"          # 租賃中
    REPAIR = "repair"          # 維修中
    DISPOSED = "disposed"      # 已報廢
    LOST = "lost"              # 遺失


class Equipment(Base, TimestampMixin):
    """設備表"""

    __tablename__ = "equipments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 資產編號與 QR Code
    asset_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    qr_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # 設備基本資訊
    category: Mapped[EquipmentCategory] = mapped_column(
        SQLEnum(EquipmentCategory),
        nullable=False,
        index=True
    )
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 狀態與位置
    status: Mapped[EquipmentStatus] = mapped_column(
        SQLEnum(EquipmentStatus),
        default=EquipmentStatus.ORDERING,
        nullable=False,
        index=True
    )
    current_location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True
    )

    # Deployment information
    deployed_to: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Vessel name or person name
    deployed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)  # Who deployed it

    # Purchase information
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Attachments
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    manual_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    calibration_report_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Maintenance records
    last_maintenance_date: Mapped[Optional[str]] = mapped_column(Date, nullable=True)
    next_maintenance_date: Mapped[Optional[str]] = mapped_column(Date, nullable=True)
    maintenance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 備註與規格
    specifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 狀態
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 關聯
    current_location: Mapped[Optional["Location"]] = relationship(
        "Location",
        back_populates="equipments",
        foreign_keys=[current_location_id]
    )
    logs: Mapped[list["EquipmentLog"]] = relationship(
        "EquipmentLog",
        back_populates="equipment",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Equipment(id={self.id}, asset_code='{self.asset_code}', status='{self.status.value}')>"
