"""Customer model"""
from typing import Optional, List
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Customer(Base, TimestampMixin):
    """Customer table"""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Basic information
    company_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)

    # Contact information
    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    rentals: Mapped[List["Rental"]] = relationship(
        "Rental",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, company='{self.company_name}')>"
