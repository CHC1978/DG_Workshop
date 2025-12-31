"""專案模型"""
import enum
from typing import Optional
from datetime import date
from sqlalchemy import String, Date, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class ProjectStatus(str, enum.Enum):
    """專案狀態"""
    PLANNING = "planning"       # 規劃中
    ACTIVE = "active"           # 進行中
    ON_HOLD = "on_hold"         # 暫停
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消


class Project(Base, TimestampMixin):
    """專案表"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 專案基本資訊
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 客戶資訊
    client_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    client_contact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    client_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    client_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 日期
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # 狀態
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.PLANNING,
        nullable=False
    )

    # 是否啟用
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # 關聯
    # vessels: 使用此專案的船舶（Location）
    vessels: Mapped[list["Location"]] = relationship(
        "Location",
        back_populates="current_project",
        foreign_keys="Location.current_project_id"
    )

    # equipment: 使用此專案的設備
    equipment: Mapped[list["Equipment"]] = relationship(
        "Equipment",
        back_populates="project",
        foreign_keys="Equipment.project_id"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, code={self.code}, name={self.name}, status={self.status})>"
