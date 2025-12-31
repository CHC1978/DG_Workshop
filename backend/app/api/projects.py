"""Project management API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.database import get_db
from app.core.deps import get_current_user, require_manager, require_admin
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.location import Location
from app.models.equipment import Equipment
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


# ==================== Helper Functions ====================

async def get_project_stats(db: AsyncSession, project_id: int) -> dict:
    """取得專案統計資料"""
    # 統計關聯船舶數量
    vessel_count_query = select(func.count(Location.id)).where(
        Location.current_project_id == project_id,
        Location.is_active == True
    )
    vessel_result = await db.execute(vessel_count_query)
    vessel_count = vessel_result.scalar() or 0

    # 統計關聯設備數量
    equipment_count_query = select(func.count(Equipment.id)).where(
        Equipment.project_id == project_id,
        Equipment.is_active == True
    )
    equipment_result = await db.execute(equipment_count_query)
    equipment_count = equipment_result.scalar() or 0

    return {
        "vessel_count": vessel_count,
        "equipment_count": equipment_count
    }


# ==================== CRUD Operations ====================

@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ProjectStatus] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取得專案列表（支援篩選與分頁）

    - **skip**: 跳過筆數
    - **limit**: 每頁筆數
    - **status**: 專案狀態篩選
    - **search**: 搜尋關鍵字（專案代碼、名稱、客戶名稱）
    - **is_active**: 是否啟用（True/False/None）
    """
    query = select(Project)

    # 應用篩選條件
    if is_active is not None:
        query = query.where(Project.is_active == is_active)

    if status:
        query = query.where(Project.status == status)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Project.code.like(search_pattern),
                Project.name.like(search_pattern),
                Project.client_name.like(search_pattern),
            )
        )

    # 取得總數
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 計算總頁數
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1

    # 取得分頁結果
    query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()

    # 為每個專案加入統計資料
    projects_with_stats = []
    for project in projects:
        stats = await get_project_stats(db, project.id)
        project_dict = ProjectResponse.model_validate(project).model_dump()
        project_dict.update(stats)
        projects_with_stats.append(ProjectResponse(**project_dict))

    return ProjectListResponse(
        projects=projects_with_stats,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    建立新專案（需要 Manager 以上權限）

    - **code**: 專案代碼（唯一）
    - **name**: 專案名稱
    - **description**: 專案描述（選填）
    - **client_name**: 客戶名稱（選填）
    - **client_contact**: 聯絡人（選填）
    - **client_phone**: 聯絡電話（選填）
    - **client_email**: 聯絡信箱（選填）
    - **start_date**: 開始日期（選填）
    - **end_date**: 結束日期（選填）
    - **status**: 專案狀態（預設為 PLANNING）
    """
    # 檢查專案代碼是否已存在
    existing_query = select(Project).where(Project.code == project_in.code)
    existing_result = await db.execute(existing_query)
    existing_project = existing_result.scalar_one_or_none()

    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project code '{project_in.code}' already exists"
        )

    # 建立專案
    project = Project(**project_in.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # 取得統計資料
    stats = await get_project_stats(db, project.id)
    project_dict = ProjectResponse.model_validate(project).model_dump()
    project_dict.update(stats)

    return ProjectResponse(**project_dict)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取得專案詳細資料

    - **project_id**: 專案 ID
    """
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 取得統計資料
    stats = await get_project_stats(db, project.id)
    project_dict = ProjectResponse.model_validate(project).model_dump()
    project_dict.update(stats)

    return ProjectResponse(**project_dict)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    更新專案資料（需要 Manager 以上權限）

    - **project_id**: 專案 ID
    - 可更新的欄位：code, name, description, client_*, start_date, end_date, status, is_active
    """
    # 取得專案
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 如果要更新 code，檢查是否與其他專案重複
    if project_in.code and project_in.code != project.code:
        existing_query = select(Project).where(
            Project.code == project_in.code,
            Project.id != project_id
        )
        existing_result = await db.execute(existing_query)
        existing_project = existing_result.scalar_one_or_none()

        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project code '{project_in.code}' already exists"
            )

    # 更新專案
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    # 取得統計資料
    stats = await get_project_stats(db, project.id)
    project_dict = ProjectResponse.model_validate(project).model_dump()
    project_dict.update(stats)

    return ProjectResponse(**project_dict)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    刪除專案（軟刪除，需要 Admin 權限）

    - **project_id**: 專案 ID
    """
    # 取得專案
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 檢查是否有關聯的船舶或設備
    stats = await get_project_stats(db, project.id)
    if stats["vessel_count"] > 0 or stats["equipment_count"] > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete project: {stats['vessel_count']} vessels and {stats['equipment_count']} equipment are still associated with this project"
        )

    # 軟刪除
    project.is_active = False
    await db.commit()

    return None
