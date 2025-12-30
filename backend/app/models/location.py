"""位置/船舶模型"""
import enum
from typing import Optional, List
from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class LocationType(str, enum.Enum):
    """位置類型"""
    WAREHOUSE = "warehouse"    # 倉庫
    VESSEL = "vessel"          # 船舶
    PLATFORM = "platform"      # 平台
    VEHICLE = "vehicle"        # 車輛
    EXTERNAL = "external"      # 外部（租賃客戶處）


class Location(Base, TimestampMixin):
    """位置/船舶表"""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 基本資訊
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location_type: Mapped[LocationType] = mapped_column(
        SQLEnum(LocationType),
        nullable=False,
        index=True
    )
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)

    # 船舶專用欄位
    imo_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    call_sign: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    owner_company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 狀態
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 關聯
    equipments: Mapped[List["Equipment"]] = relationship(
        "Equipment",
        back_populates="current_location",
        foreign_keys="Equipment.current_location_id"
    )

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, name='{self.name}', type='{self.location_type.value}')>"
