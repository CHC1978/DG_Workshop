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
    ORDERING = "ordering"          # 採購中
    IN_STOCK = "in_stock"          # 庫存中
    DEPLOYED = "deployed"          # 自用部署中
    RENTED = "rented"              # 租賃中
    REPAIR = "repair"              # 維修中
    CALIBRATING = "calibrating"    # 校正中
    DISPOSED = "disposed"          # 已報廢
    LOST = "lost"                  # 遺失


class InstallationType(str, enum.Enum):
    """安裝類型"""
    PERMANENT = "permanent"        # 永久安裝
    PROJECT = "project"            # 專案臨時安裝
    TEMPORARY = "temporary"        # 暫時安裝


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
    model_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
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

    # 設備負責人（從 Location type=person 合併後新增）
    assigned_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Project 關聯
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Parent-Child Equipment Relationship (for sub-components)
    parent_equipment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("equipments.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Installation information
    installation_type: Mapped[Optional[InstallationType]] = mapped_column(
        SQLEnum(InstallationType),
        nullable=True
    )
    installation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    installation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="equipment",
        foreign_keys=[project_id]
    )
    logs: Mapped[list["EquipmentLog"]] = relationship(
        "EquipmentLog",
        back_populates="equipment",
        cascade="all, delete-orphan"
    )

    # 設備負責人關聯
    assigned_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_user_id],
        backref="assigned_equipment"
    )

    # Parent-Child relationships (self-referential)
    parent: Mapped[Optional["Equipment"]] = relationship(
        "Equipment",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_equipment_id]
    )
    children: Mapped[list["Equipment"]] = relationship(
        "Equipment",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_equipment_id]
    )

    # Legacy sub_equipments (will be removed after migration)
    sub_equipments: Mapped[list["SubEquipment"]] = relationship(
        "SubEquipment",
        back_populates="parent_equipment",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Equipment(id={self.id}, asset_code='{self.asset_code}', status='{self.status.value}')>"
