"""File upload API endpoints"""
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.equipment import Equipment

router = APIRouter(prefix="/uploads", tags=["File Uploads"])

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_equipment_upload_dir(asset_code: str) -> Path:
    """Get or create equipment upload directory"""
    equipment_dir = UPLOAD_DIR / asset_code
    equipment_dir.mkdir(parents=True, exist_ok=True)
    return equipment_dir


def validate_file_extension(filename: str, file_type: str) -> str:
    """Validate file extension based on type"""
    ext = Path(filename).suffix.lower()

    if file_type == "photo":
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image format. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            )
    elif file_type in ["manual", "report"]:
        if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document format. Allowed: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"
            )

    return ext


@router.post("/equipment/{equipment_id}/photo")
async def upload_equipment_photo(
    equipment_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload equipment photo"""
    # Get equipment
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    ext = validate_file_extension(file.filename, "photo")

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Save file
    upload_dir = get_equipment_upload_dir(equipment.asset_code)
    filename = f"photo{ext}"
    file_path = upload_dir / filename

    # Remove old photo if exists
    if file_path.exists():
        file_path.unlink()

    # Save new file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Update equipment record
    relative_path = f"/uploads/{equipment.asset_code}/{filename}"
    equipment.photo_url = relative_path
    await db.commit()

    return {
        "message": "Photo uploaded successfully",
        "url": relative_path,
        "filename": filename
    }


@router.post("/equipment/{equipment_id}/manual")
async def upload_equipment_manual(
    equipment_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload equipment manual (PDF)"""
    # Get equipment
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    ext = validate_file_extension(file.filename, "manual")

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Save file
    upload_dir = get_equipment_upload_dir(equipment.asset_code)
    filename = f"manual{ext}"
    file_path = upload_dir / filename

    # Remove old manual if exists
    if file_path.exists():
        file_path.unlink()

    # Save new file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Update equipment record
    relative_path = f"/uploads/{equipment.asset_code}/{filename}"
    equipment.manual_url = relative_path
    await db.commit()

    return {
        "message": "Manual uploaded successfully",
        "url": relative_path,
        "filename": filename
    }


@router.post("/equipment/{equipment_id}/calibration-report")
async def upload_calibration_report(
    equipment_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload calibration report (PDF)"""
    # Get equipment
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    ext = validate_file_extension(file.filename, "report")

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Save file
    upload_dir = get_equipment_upload_dir(equipment.asset_code)
    filename = f"calibration_report{ext}"
    file_path = upload_dir / filename

    # Remove old report if exists
    if file_path.exists():
        file_path.unlink()

    # Save new file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Update equipment record
    relative_path = f"/uploads/{equipment.asset_code}/{filename}"
    equipment.calibration_report_url = relative_path
    await db.commit()

    return {
        "message": "Calibration report uploaded successfully",
        "url": relative_path,
        "filename": filename
    }


@router.delete("/equipment/{equipment_id}/photo")
async def delete_equipment_photo(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete equipment photo"""
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment or not equipment.photo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Delete file
    file_path = Path(equipment.photo_url.lstrip('/'))
    if file_path.exists():
        file_path.unlink()

    # Clear URL from database
    equipment.photo_url = None
    await db.commit()

    return {"message": "Photo deleted successfully"}


@router.delete("/equipment/{equipment_id}/manual")
async def delete_equipment_manual(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete equipment manual"""
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment or not equipment.manual_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manual not found"
        )

    # Delete file
    file_path = Path(equipment.manual_url.lstrip('/'))
    if file_path.exists():
        file_path.unlink()

    # Clear URL from database
    equipment.manual_url = None
    await db.commit()

    return {"message": "Manual deleted successfully"}


@router.delete("/equipment/{equipment_id}/calibration-report")
async def delete_calibration_report(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete calibration report"""
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment or not equipment.calibration_report_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Delete file
    file_path = Path(equipment.calibration_report_url.lstrip('/'))
    if file_path.exists():
        file_path.unlink()

    # Clear URL from database
    equipment.calibration_report_url = None
    await db.commit()

    return {"message": "Calibration report deleted successfully"}


@router.get("/equipment/{asset_code}/files")
async def list_equipment_files(
    asset_code: str,
    current_user: User = Depends(get_current_user)
):
    """List all files for an equipment"""
    upload_dir = UPLOAD_DIR / asset_code

    if not upload_dir.exists():
        return {"files": []}

    files = []
    for file_path in upload_dir.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "name": file_path.name,
                "size": stat.st_size,
                "url": f"/uploads/{asset_code}/{file_path.name}",
                "modified": stat.st_mtime
            })

    return {"files": files}
