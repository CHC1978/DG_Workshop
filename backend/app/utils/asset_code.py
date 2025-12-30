"""Asset code generation utilities"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.equipment import Equipment, EquipmentCategory


async def generate_asset_code(
    category: EquipmentCategory,
    db: AsyncSession,
    year: int = None
) -> str:
    """
    Generate unique asset code for equipment

    Format: {CATEGORY}-{YEAR}-{SEQUENCE}
    Example: MBES-2024-001, GNSS-2023-015

    Args:
        category: Equipment category
        db: Database session
        year: Year for the asset code (default: current year)

    Returns:
        Asset code string
    """
    if year is None:
        year = datetime.now().year

    # Get category prefix (uppercase)
    category_prefix = category.value.upper()

    # Find the highest sequence number for this category and year
    # Pattern: {CATEGORY}-{YEAR}-{SEQUENCE}
    pattern = f"{category_prefix}-{year}-%"

    result = await db.execute(
        select(func.count(Equipment.id))
        .where(Equipment.asset_code.like(pattern))
    )
    count = result.scalar()

    # Next sequence number (001, 002, 003, ...)
    next_sequence = count + 1

    # Format: CATEGORY-YEAR-SEQUENCE (3 digits)
    asset_code = f"{category_prefix}-{year}-{next_sequence:03d}"

    return asset_code


def generate_qr_code_url(asset_code: str, domain: str = None) -> str:
    """
    Generate QR code URL for equipment

    Args:
        asset_code: Equipment asset code
        domain: Domain name (default: localhost for development)

    Returns:
        QR code URL string
    """
    if domain is None:
        domain = "localhost:5173"

    return f"https://{domain}/e/{asset_code}"
