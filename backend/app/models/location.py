"""位置/船舶模型"""
import enum
from typing import Optional, List
from sqlalchemy import String, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class LocationType(str, enum.Enum):
    """位置類型"""
    WAREHOUSE = "warehouse"    # 倉庫
    VESSEL = "vessel"          # 船舶
    PERSON = "person"          # 人員
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

    # 船舶專用欄位 - 識別碼
    imo_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    vessel_mmsi: Mapped[Optional[str]] = mapped_column(String(9), nullable=True)
    vessel_national_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    vessel_internal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    call_sign: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # 船舶專用欄位 - 詳細資訊
    vessel_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    vessel_flag: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    vessel_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    vessel_owner: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    owner_company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Person 專用欄位
    person_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    person_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 通用圖片欄位 (Vessel photo, Person photo)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Warehouse 專用欄位
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 聯繫人關聯 (舊欄位 - 指向 Location type=person，待遷移後移除)
    contact_person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # 聯繫人關聯 (新欄位 - 指向 User，Person 合併到 User 後使用)
    contact_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Project 關聯
    current_project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # 狀態
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 關聯
    equipments: Mapped[List["Equipment"]] = relationship(
        "Equipment",
        back_populates="current_location",
        foreign_keys="Equipment.current_location_id"
    )

    current_project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="vessels",
        foreign_keys=[current_project_id]
    )

    # 聯繫人關聯 (self-referential - 舊，待遷移後移除)
    contact_person: Mapped[Optional["Location"]] = relationship(
        "Location",
        remote_side=[id],
        foreign_keys=[contact_person_id]
    )

    # 聯繫人關聯 (新 - 指向 User)
    contact_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[contact_user_id],
        backref="contact_for_locations"
    )

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, name='{self.name}', type='{self.location_type.value}')>"
