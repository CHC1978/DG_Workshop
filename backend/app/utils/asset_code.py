"""Asset code generation utilities"""
import re
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.equipment import Equipment, EquipmentCategory
from app.models.sub_equipment import SubEquipment


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


def clean_model_code(model: str) -> str:
    """
    Clean model name to create a compact model code

    Rules:
    - Remove special characters except hyphen and underscore
    - Remove spaces
    - Convert to uppercase
    - Limit to 20 characters

    Args:
        model: Equipment model name

    Returns:
        Cleaned model code string

    Examples:
        "EM 2040C" -> "EM2040C"
        "Seapath 330+" -> "SEAPATH330"
        "EdgeTech 4200" -> "EDGETECH4200"
    """
    # Remove special characters except hyphen and underscore
    cleaned = re.sub(r'[^a-zA-Z0-9\-_]', '', model)

    # Convert to uppercase
    cleaned = cleaned.upper()

    # Limit to 20 characters
    if len(cleaned) > 20:
        cleaned = cleaned[:20]

    return cleaned


async def generate_asset_code_v2(
    category: EquipmentCategory,
    model_code: str,
    db: AsyncSession,
    serial_number: str = None
) -> str:
    """
    Generate unique asset code for equipment (v2 format)

    Format:
    - With serial number: {CATEGORY}-{MODEL_CODE}-SN{SERIAL}
    - Without serial number: {CATEGORY}-{MODEL_CODE}-{SEQUENCE}

    Examples:
        MBES-EM2040C-SN12345
        GNSS-SEAPATH330-0001

    Args:
        category: Equipment category
        model_code: Cleaned model code (use clean_model_code() first)
        db: Database session
        serial_number: Serial number (optional)

    Returns:
        Asset code string
    """
    # Get category prefix (uppercase)
    category_prefix = category.value.upper()

    # Clean model code
    model_code_clean = clean_model_code(model_code)

    # If serial number is provided, use it directly
    if serial_number:
        asset_code = f"{category_prefix}-{model_code_clean}-SN{serial_number}"
        return asset_code

    # Otherwise, generate sequence number
    # Pattern: {CATEGORY}-{MODEL_CODE}-%
    pattern = f"{category_prefix}-{model_code_clean}-%"

    result = await db.execute(
        select(func.count(Equipment.id))
        .where(Equipment.asset_code.like(pattern))
    )
    count = result.scalar()

    # Next sequence number (0001, 0002, 0003, ...)
    next_sequence = count + 1

    # Format: CATEGORY-MODELCODE-SEQUENCE (4 digits)
    asset_code = f"{category_prefix}-{model_code_clean}-{next_sequence:04d}"

    return asset_code


def generate_qr_code_url(asset_code: str, domain: str = None, protocol: str = None) -> str:
    """
    Generate QR code URL for equipment

    Args:
        asset_code: Equipment asset code
        domain: Domain name (default: from settings)
        protocol: http or https (default: from settings)

    Returns:
        QR code URL string
    """
    if domain is None or protocol is None:
        from app.core.config import settings
        domain = domain or settings.QR_CODE_DOMAIN
        protocol = protocol or settings.QR_CODE_PROTOCOL

    return f"{protocol}://{domain}/e/{asset_code}"


async def generate_sub_equipment_asset_code(
    parent_asset_code: str,
    db: AsyncSession
) -> str:
    """
    Generate unique asset code for sub-equipment

    Format: {PARENT_ASSET_CODE}-{SUB_SEQUENCE}
    Example: MBES-2024-001-01, MBES-2024-001-02

    Args:
        parent_asset_code: Parent equipment asset code
        db: Database session

    Returns:
        Sub-equipment asset code string
    """
    # Find the highest sequence number for this parent
    pattern = f"{parent_asset_code}-%"

    result = await db.execute(
        select(func.count(SubEquipment.id))
        .where(SubEquipment.asset_code.like(pattern))
    )
    count = result.scalar()

    # Next sequence number (01, 02, 03, ...)
    next_sequence = count + 1

    # Format: PARENT-SEQUENCE (2 digits)
    asset_code = f"{parent_asset_code}-{next_sequence:02d}"

    return asset_code
