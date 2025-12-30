"""QR Code generation API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import qrcode
import io

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.equipment import Equipment
from app.schemas.equipment import QRCodeResponse
from app.utils.asset_code import generate_qr_code_url

router = APIRouter(prefix="/qrcode", tags=["QR Code"])


@router.get("/{equipment_id}", response_model=QRCodeResponse)
async def get_qrcode_info(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get QR code information for equipment (base64 encoded)
    """
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(equipment.qr_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    import base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return QRCodeResponse(
        asset_code=equipment.asset_code,
        qr_code_url=equipment.qr_code,
        qr_code_base64=f"data:image/png;base64,{img_base64}"
    )


@router.get("/{equipment_id}/image")
async def get_qrcode_image(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get QR code image (PNG) for equipment
    Returns image file for download/printing
    """
    result = await db.execute(
        select(Equipment).where(Equipment.id == equipment_id)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(equipment.qr_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename={equipment.asset_code}.png"
        }
    )


@router.get("/by-asset/{asset_code}/image")
async def get_qrcode_image_by_asset_code(
    asset_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get QR code image by asset code
    Useful for batch printing
    """
    result = await db.execute(
        select(Equipment).where(Equipment.asset_code == asset_code)
    )
    equipment = result.scalar_one_or_none()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment not found: {asset_code}",
        )

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(equipment.qr_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename={asset_code}.png"
        }
    )
