"""專案 Schema"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    """專案基礎 Schema"""
    code: str = Field(..., min_length=1, max_length=30, description="專案代碼")
    name: str = Field(..., min_length=1, max_length=100, description="專案名稱")
    description: Optional[str] = Field(None, max_length=2000, description="專案描述")

    # 客戶資訊
    client_name: Optional[str] = Field(None, max_length=100, description="客戶名稱")
    client_contact: Optional[str] = Field(None, max_length=50, description="聯絡人")
    client_phone: Optional[str] = Field(None, max_length=20, description="聯絡電話")
    client_email: Optional[str] = Field(None, max_length=100, description="聯絡信箱")

    # 日期
    start_date: Optional[date] = Field(None, description="開始日期")
    end_date: Optional[date] = Field(None, description="結束日期")

    # 狀態
    status: ProjectStatus = Field(ProjectStatus.PLANNING, description="專案狀態")


class ProjectCreate(ProjectBase):
    """建立專案 Schema"""
    pass


class ProjectUpdate(BaseModel):
    """更新專案 Schema"""
    code: Optional[str] = Field(None, min_length=1, max_length=30)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)

    client_name: Optional[str] = Field(None, max_length=100)
    client_contact: Optional[str] = Field(None, max_length=50)
    client_phone: Optional[str] = Field(None, max_length=20)
    client_email: Optional[str] = Field(None, max_length=100)

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ProjectStatus] = None
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """專案回應 Schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # 統計資訊
    vessel_count: int = Field(0, description="關聯船舶數量")
    equipment_count: int = Field(0, description="關聯設備數量")

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """專案列表回應 Schema"""
    projects: list[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
