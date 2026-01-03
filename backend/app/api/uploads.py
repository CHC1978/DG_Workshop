"""File upload API endpoints"""
import os
import re
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.equipment import Equipment
from app.models.location import Location
from app.utils.file_validator import (
    FileValidator,
    ValidationStatus,
    validate_upload,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uploads", tags=["File Uploads"])

# 從 main.py 獲取 limiter
from app.main import limiter

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file extensions and MIME types
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# MIME type 白名單
ALLOWED_IMAGE_MIMES = {
    "image/jpeg", "image/png", "image/gif", "image/webp"
}
ALLOWED_DOCUMENT_MIMES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}


def get_equipment_upload_dir(asset_code: str) -> Path:
    """Get or create equipment upload directory"""
    equipment_dir = UPLOAD_DIR / asset_code
    equipment_dir.mkdir(parents=True, exist_ok=True)
    return equipment_dir


def get_location_upload_dir(location_id: int) -> Path:
    """Get or create location upload directory"""
    location_dir = UPLOAD_DIR / "locations" / str(location_id)
    location_dir.mkdir(parents=True, exist_ok=True)
    return location_dir


def get_user_upload_dir(user_id: int) -> Path:
    """Get or create user upload directory"""
    user_dir = UPLOAD_DIR / "users" / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


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


def validate_mime_type(content_type: Optional[str], file_type: str) -> None:
    """
    驗證檔案 MIME 類型

    Args:
        content_type: 上傳檔案的 Content-Type
        file_type: 檔案類型 (photo, manual, report)

    Raises:
        HTTPException: 如果 MIME 類型不在白名單中
    """
    if not content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Type header is required"
        )

    # 移除可能的 charset 參數
    mime = content_type.split(';')[0].strip().lower()

    if file_type == "photo":
        if mime not in ALLOWED_IMAGE_MIMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image MIME type: {mime}. Allowed: {', '.join(ALLOWED_IMAGE_MIMES)}"
            )
    elif file_type in ["manual", "report"]:
        if mime not in ALLOWED_DOCUMENT_MIMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document MIME type: {mime}. Allowed: {', '.join(ALLOWED_DOCUMENT_MIMES)}"
            )


def safe_delete_file(file_url: str) -> None:
    """
    安全刪除檔案,防止路徑遍歷攻擊

    Args:
        file_url: 檔案 URL 路徑

    Raises:
        HTTPException: 如果路徑不安全
    """
    if not file_url:
        return

    # 解析路徑
    file_path = Path(file_url.lstrip('/'))

    # 解析為絕對路徑
    try:
        file_path_resolved = file_path.resolve()
        uploads_dir_resolved = UPLOAD_DIR.resolve()

        # 驗證路徑在 uploads 目錄內
        if not str(file_path_resolved).startswith(str(uploads_dir_resolved)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path detected"
            )

        # 安全刪除
        if file_path_resolved.exists():
            file_path_resolved.unlink()
    except (ValueError, OSError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.post("/equipment/{equipment_id}/photo")
@limiter.limit("20/minute")  # 上傳操作限制
async def upload_equipment_photo(
    request: Request,
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
    validate_mime_type(file.content_type, "photo")

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Read file content for validation
    file_content = await file.read()

    # Validate file with magic number check and sanitization
    processed_content, validation_result = validate_upload(
        file_content=file_content,
        filename=file.filename,
        file_type="image",
        sanitize=True
    )

    if validation_result.status == ValidationStatus.INVALID_SIGNATURE:
        logger.warning(f"Invalid file signature for photo upload: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {validation_result.message}"
        )

    if validation_result.status == ValidationStatus.SUSPICIOUS_CONTENT:
        logger.warning(f"Suspicious content in photo: {file.filename} - {validation_result.warnings}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File rejected: {validation_result.message}"
        )

    # Log if image was sanitized
    if validation_result.sanitized:
        logger.info(f"Image sanitized: {file.filename} for equipment {equipment.asset_code}")

    # Save file
    upload_dir = get_equipment_upload_dir(equipment.asset_code)
    filename = f"photo{ext}"
    file_path = upload_dir / filename

    # Remove old photo if exists
    if file_path.exists():
        file_path.unlink()

    # Save processed file (sanitized if applicable)
    with open(file_path, "wb") as f:
        f.write(processed_content)

    # Update equipment record
    relative_path = f"/uploads/{equipment.asset_code}/{filename}"
    equipment.photo_url = relative_path
    await db.commit()

    return {
        "message": "Photo uploaded successfully",
        "url": relative_path,
        "filename": filename,
        "sanitized": validation_result.sanitized,
        "warnings": validation_result.warnings if validation_result.warnings else None
    }


@router.post("/equipment/{equipment_id}/manual")
@limiter.limit("20/minute")
async def upload_equipment_manual(
    request: Request,
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
    validate_mime_type(file.content_type, "manual")

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Read file content for validation
    file_content = await file.read()

    # Determine validation type based on extension
    validation_type = "pdf" if ext == ".pdf" else "document"

    # Validate file with magic number check
    processed_content, validation_result = validate_upload(
        file_content=file_content,
        filename=file.filename,
        file_type=validation_type,
        sanitize=False
    )

    if validation_result.status == ValidationStatus.INVALID_SIGNATURE:
        logger.warning(f"Invalid file signature for manual upload: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {validation_result.message}"
        )

    if validation_result.status == ValidationStatus.SUSPICIOUS_CONTENT:
        logger.warning(f"Suspicious content in manual: {file.filename} - {validation_result.warnings}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File rejected for security reasons: {validation_result.message}"
        )

    # Log warnings if any
    if validation_result.warnings:
        logger.info(f"Document warnings for {file.filename}: {validation_result.warnings}")

    # Save file
    upload_dir = get_equipment_upload_dir(equipment.asset_code)
    filename = f"manual{ext}"
    file_path = upload_dir / filename

    # Remove old manual if exists
    if file_path.exists():
        file_path.unlink()

    # Save file
    with open(file_path, "wb") as f:
        f.write(processed_content)

    # Update equipment record
    relative_path = f"/uploads/{equipment.asset_code}/{filename}"
    equipment.manual_url = relative_path
    await db.commit()

    return {
        "message": "Manual uploaded successfully",
        "url": relative_path,
        "filename": filename,
        "warnings": validation_result.warnings if validation_result.warnings else None
    }


@router.post("/equipment/{equipment_id}/calibration-report")
@limiter.limit("20/minute")
async def upload_calibration_report(
    request: Request,
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
    validate_mime_type(file.content_type, "report")

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Read file content for validation
    file_content = await file.read()

    # Determine validation type based on extension
    validation_type = "pdf" if ext == ".pdf" else "document"

    # Validate file with magic number check
    processed_content, validation_result = validate_upload(
        file_content=file_content,
        filename=file.filename,
        file_type=validation_type,
        sanitize=False
    )

    if validation_result.status == ValidationStatus.INVALID_SIGNATURE:
        logger.warning(f"Invalid file signature for calibration report: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {validation_result.message}"
        )

    if validation_result.status == ValidationStatus.SUSPICIOUS_CONTENT:
        logger.warning(f"Suspicious content in calibration report: {file.filename} - {validation_result.warnings}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File rejected for security reasons: {validation_result.message}"
        )

    # Log warnings if any
    if validation_result.warnings:
        logger.info(f"Document warnings for {file.filename}: {validation_result.warnings}")

    # Save file
    upload_dir = get_equipment_upload_dir(equipment.asset_code)
    filename = f"calibration_report{ext}"
    file_path = upload_dir / filename

    # Remove old report if exists
    if file_path.exists():
        file_path.unlink()

    # Save file
    with open(file_path, "wb") as f:
        f.write(processed_content)

    # Update equipment record
    relative_path = f"/uploads/{equipment.asset_code}/{filename}"
    equipment.calibration_report_url = relative_path
    await db.commit()

    return {
        "message": "Calibration report uploaded successfully",
        "url": relative_path,
        "filename": filename,
        "warnings": validation_result.warnings if validation_result.warnings else None
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

    # Delete file (使用安全刪除函數)
    safe_delete_file(equipment.photo_url)

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

    # Delete file (使用安全刪除函數)
    safe_delete_file(equipment.manual_url)

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

    # Delete file (使用安全刪除函數)
    safe_delete_file(equipment.calibration_report_url)

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
    # 驗證 asset_code 格式 (例如: MBES-2024-001)
    if not re.match(r'^[A-Z]+-\d{4}-\d{3}$', asset_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid asset code format"
        )

    # 使用白名單驗證
    upload_dir = UPLOAD_DIR / asset_code

    # 解析並驗證路徑
    try:
        upload_dir_resolved = upload_dir.resolve()
        uploads_dir_resolved = UPLOAD_DIR.resolve()

        # 確保路徑在 UPLOAD_DIR 內
        if not str(upload_dir_resolved).startswith(str(uploads_dir_resolved)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid path"
            )
    except (ValueError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid path"
        )

    if not upload_dir_resolved.exists():
        return {"files": []}

    files = []
    for file_path in upload_dir_resolved.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "name": file_path.name,
                "size": stat.st_size,
                "url": f"/uploads/{asset_code}/{file_path.name}",
                "modified": stat.st_mtime
            })

    return {"files": files}


# ==================== Calibration Report Upload ====================

@router.post("/calibrations/{calibration_id}/report")
@limiter.limit("20/minute")
async def upload_calibration_report_file(
    request: Request,
    calibration_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload calibration report file"""
    from app.models.calibration import Calibration

    # Get calibration
    result = await db.execute(
        select(Calibration).where(Calibration.id == calibration_id)
    )
    calibration = result.scalar_one_or_none()

    if not calibration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calibration not found"
        )

    # Get equipment to determine directory
    result = await db.execute(
        select(Equipment).where(Equipment.id == calibration.equipment_id)
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
    validate_mime_type(file.content_type, "report")

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Read file content for validation
    file_content = await file.read()

    # Determine validation type based on extension
    validation_type = "pdf" if ext == ".pdf" else "document"

    # Validate file with magic number check
    processed_content, validation_result = validate_upload(
        file_content=file_content,
        filename=file.filename,
        file_type=validation_type,
        sanitize=False
    )

    if validation_result.status == ValidationStatus.INVALID_SIGNATURE:
        logger.warning(f"Invalid file signature for calibration report: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {validation_result.message}"
        )

    if validation_result.status == ValidationStatus.SUSPICIOUS_CONTENT:
        logger.warning(f"Suspicious content in calibration report: {file.filename} - {validation_result.warnings}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File rejected for security reasons: {validation_result.message}"
        )

    # Log warnings if any
    if validation_result.warnings:
        logger.info(f"Document warnings for {file.filename}: {validation_result.warnings}")

    # Save file
    upload_dir = get_equipment_upload_dir(equipment.asset_code)
    filename = f"calibration_{calibration_id}{ext}"
    file_path = upload_dir / filename

    # Remove old file if exists
    if file_path.exists():
        file_path.unlink()

    # Save file
    with open(file_path, "wb") as f:
        f.write(processed_content)

    # Update calibration record
    relative_path = f"/uploads/{equipment.asset_code}/{filename}"
    calibration.report_url = relative_path
    await db.commit()

    return {
        "message": "Calibration report uploaded successfully",
        "url": relative_path,
        "filename": filename,
        "warnings": validation_result.warnings if validation_result.warnings else None
    }


@router.delete("/calibrations/{calibration_id}/report")
async def delete_calibration_report_by_calibration(
    calibration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete calibration report"""
    from app.models.calibration import Calibration

    result = await db.execute(
        select(Calibration).where(Calibration.id == calibration_id)
    )
    calibration = result.scalar_one_or_none()

    if not calibration or not calibration.report_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Delete file (使用安全刪除函數)
    safe_delete_file(calibration.report_url)

    # Clear URL from database
    calibration.report_url = None
    await db.commit()

    return {"message": "Calibration report deleted successfully"}


# ==================== Equipment Log Attachment Upload ====================

@router.post("/equipment-logs/{log_id}/attachments")
@limiter.limit("20/minute")
async def upload_log_attachment(
    request: Request,
    log_id: int,
    file: UploadFile = File(...),
    attachment_type: str = "other",
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload attachment to equipment log"""
    from app.models.equipment_log import EquipmentLog
    from app.models.log_attachment import LogAttachment, AttachmentType

    # Get log
    result = await db.execute(
        select(EquipmentLog).where(EquipmentLog.id == log_id)
    )
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment log not found"
        )

    # Get equipment
    result = await db.execute(
        select(Equipment).where(Equipment.id == log.equipment_id)
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

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Read file content for validation
    file_content = await file.read()

    # Determine file type based on extension
    ext = Path(file.filename).suffix.lower()
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        validation_type = "image"
        sanitize = True
    elif ext == ".pdf":
        validation_type = "pdf"
        sanitize = False
    elif ext in ALLOWED_DOCUMENT_EXTENSIONS:
        validation_type = "document"
        sanitize = False
    else:
        # For other file types, just do basic magic number check
        validation_type = None
        sanitize = False

    # Validate file if we have a known type
    processed_content = file_content
    validation_warnings = []

    if validation_type:
        processed_content, validation_result = validate_upload(
            file_content=file_content,
            filename=file.filename,
            file_type=validation_type,
            sanitize=sanitize
        )

        if validation_result.status == ValidationStatus.INVALID_SIGNATURE:
            logger.warning(f"Invalid file signature for log attachment: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format: {validation_result.message}"
            )

        if validation_result.status == ValidationStatus.SUSPICIOUS_CONTENT:
            logger.warning(f"Suspicious content in log attachment: {file.filename} - {validation_result.warnings}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File rejected for security reasons: {validation_result.message}"
            )

        validation_warnings = validation_result.warnings or []

    # Save file
    log_dir = UPLOAD_DIR / equipment.asset_code / "logs" / str(log_id)
    log_dir.mkdir(parents=True, exist_ok=True)

    import time
    timestamp = int(time.time())
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = log_dir / safe_filename

    with open(file_path, "wb") as f:
        f.write(processed_content)

    # Create attachment record
    relative_path = f"/uploads/{equipment.asset_code}/logs/{log_id}/{safe_filename}"

    attachment = LogAttachment(
        equipment_log_id=log_id,
        file_url=relative_path,
        file_name=file.filename,
        file_type=AttachmentType(attachment_type) if attachment_type in [e.value for e in AttachmentType] else AttachmentType.OTHER,
        file_size=file_size,
        description=description,
        uploaded_by=current_user.id
    )

    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)

    return {
        "id": attachment.id,
        "message": "Attachment uploaded successfully",
        "url": relative_path,
        "filename": safe_filename,
        "warnings": validation_warnings if validation_warnings else None
    }


@router.get("/equipment-logs/{log_id}/attachments")
async def list_log_attachments(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all attachments for a log"""
    from app.models.log_attachment import LogAttachment

    result = await db.execute(
        select(LogAttachment).where(LogAttachment.equipment_log_id == log_id)
    )
    attachments = result.scalars().all()

    return [{
        "id": att.id,
        "file_url": att.file_url,
        "file_name": att.file_name,
        "file_type": att.file_type.value,
        "file_size": att.file_size,
        "description": att.description,
        "created_at": att.created_at
    } for att in attachments]


@router.delete("/log-attachments/{attachment_id}")
async def delete_log_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete log attachment"""
    from app.models.log_attachment import LogAttachment

    result = await db.execute(
        select(LogAttachment).where(LogAttachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    # Delete file (使用安全刪除函數)
    safe_delete_file(attachment.file_url)

    # Delete record
    await db.delete(attachment)
    await db.commit()

    return {"message": "Attachment deleted successfully"}


# ==================== Location Photo Upload ====================

@router.post("/locations/{location_id}/photo")
@limiter.limit("20/minute")
async def upload_location_photo(
    request: Request,
    location_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload location photo (for Vessel or Person)"""
    # Get location
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    ext = validate_file_extension(file.filename, "photo")
    validate_mime_type(file.content_type, "photo")

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Read file content for validation
    file_content = await file.read()

    # Validate file with magic number check and sanitization
    processed_content, validation_result = validate_upload(
        file_content=file_content,
        filename=file.filename,
        file_type="image",
        sanitize=True
    )

    if validation_result.status == ValidationStatus.INVALID_SIGNATURE:
        logger.warning(f"Invalid file signature for location photo: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {validation_result.message}"
        )

    if validation_result.status == ValidationStatus.SUSPICIOUS_CONTENT:
        logger.warning(f"Suspicious content in location photo: {file.filename} - {validation_result.warnings}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File rejected: {validation_result.message}"
        )

    # Log if image was sanitized
    if validation_result.sanitized:
        logger.info(f"Image sanitized: {file.filename} for location {location.name}")

    # Save file
    upload_dir = get_location_upload_dir(location_id)
    filename = f"photo{ext}"
    file_path = upload_dir / filename

    # Remove old photo if exists
    if file_path.exists():
        file_path.unlink()

    # Save processed file
    with open(file_path, "wb") as f:
        f.write(processed_content)

    # Update location record
    relative_path = f"/uploads/locations/{location_id}/{filename}"
    location.photo_url = relative_path
    await db.commit()

    return {
        "message": "Photo uploaded successfully",
        "url": relative_path,
        "filename": filename,
        "sanitized": validation_result.sanitized,
        "warnings": validation_result.warnings if validation_result.warnings else None
    }


@router.delete("/locations/{location_id}/photo")
async def delete_location_photo(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete location photo"""
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location or not location.photo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Delete file
    safe_delete_file(location.photo_url)

    # Clear URL from database
    location.photo_url = None
    await db.commit()

    return {"message": "Photo deleted successfully"}


# ==================== User Photo Upload ====================

@router.post("/users/{user_id}/photo")
@limiter.limit("20/minute")
async def upload_user_photo(
    request: Request,
    user_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload user photo (avatar)"""
    # Check permission: only self or admin can upload photo
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload photo for this user"
        )

    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    ext = validate_file_extension(file.filename, "photo")
    validate_mime_type(file.content_type, "photo")

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Read file content for validation
    file_content = await file.read()

    # Validate file with magic number check and sanitization
    processed_content, validation_result = validate_upload(
        file_content=file_content,
        filename=file.filename,
        file_type="image",
        sanitize=True
    )

    if validation_result.status == ValidationStatus.INVALID_SIGNATURE:
        logger.warning(f"Invalid file signature for user photo: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {validation_result.message}"
        )

    if validation_result.status == ValidationStatus.SUSPICIOUS_CONTENT:
        logger.warning(f"Suspicious content in user photo: {file.filename} - {validation_result.warnings}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File rejected: {validation_result.message}"
        )

    # Log if image was sanitized
    if validation_result.sanitized:
        logger.info(f"Image sanitized: {file.filename} for user {user.username}")

    # Save file
    upload_dir = get_user_upload_dir(user_id)
    filename = f"photo{ext}"
    file_path = upload_dir / filename

    # Remove old photo if exists
    if file_path.exists():
        file_path.unlink()

    # Save processed file
    with open(file_path, "wb") as f:
        f.write(processed_content)

    # Update user record
    relative_path = f"/uploads/users/{user_id}/{filename}"
    user.photo_url = relative_path
    await db.commit()

    return {
        "message": "Photo uploaded successfully",
        "url": relative_path,
        "filename": filename,
        "sanitized": validation_result.sanitized,
        "warnings": validation_result.warnings if validation_result.warnings else None
    }


@router.delete("/users/{user_id}/photo")
async def delete_user_photo(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user photo"""
    # Check permission: only self or admin can delete photo
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete photo for this user"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.photo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Delete file
    safe_delete_file(user.photo_url)

    # Clear URL from database
    user.photo_url = None
    await db.commit()

    return {"message": "Photo deleted successfully"}
