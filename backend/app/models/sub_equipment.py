"""SubEquipment model - 子設備模型"""
from typing import Optional
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.equipment import EquipmentStatus


class SubEquipment(Base, TimestampMixin):
    """
    子設備表 - 用於追蹤主設備的組成部件

    每個子設備有獨立的：
    - asset_code（格式：父設備碼-子序號，如 MBES-2024-001-01）
    - QR code
    - 狀態流轉
    - 維修記錄（透過 EquipmentLog，使用 is_sub_equipment=True 標記）

    使用場景：
    - POSMV320 包含：2個天線、2條纜線、1條 IMU Cable、IMU主機
    - 每個組件可單獨追蹤序號、狀態、維修記錄
    """

    __tablename__ = "sub_equipments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 父設備關聯
    parent_equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="父設備 ID"
    )

    # 資產編號與 QR Code（格式：父設備碼-子序號）
    asset_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="資產編號，格式：父設備碼-子序號（例如：MBES-2024-001-01）"
    )
    qr_code: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="QR Code URL"
    )

    # 子設備資訊
    component_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="組件名稱（例如：天線1、IMU Cable、IMU主機）"
    )
    serial_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="序號"
    )

    # 狀態（複用 EquipmentStatus）
    status: Mapped[EquipmentStatus] = mapped_column(
        SQLEnum(EquipmentStatus),
        default=EquipmentStatus.IN_STOCK,
        nullable=False,
        index=True,
        comment="狀態"
    )

    # 備註
    notes: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="備註"
    )

    # 狀態
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        comment="是否啟用（軟刪除）"
    )

    # 關聯
    parent_equipment: Mapped["Equipment"] = relationship(
        "Equipment",
        back_populates="sub_equipments",
        foreign_keys=[parent_equipment_id]
    )

    def __repr__(self) -> str:
        return f"<SubEquipment(id={self.id}, asset_code='{self.asset_code}', component_name='{self.component_name}', parent_id={self.parent_equipment_id})>"
