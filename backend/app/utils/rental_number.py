"""Rental number generation utilities"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.rental import Rental


async def generate_rental_number(db: AsyncSession, year: int = None) -> str:
    """
    Generate unique rental number

    Format: R-{YEAR}-{SEQUENCE}
    Example: R-2025-001, R-2025-015

    Args:
        db: Database session
        year: Year for the rental number (default: current year)

    Returns:
        Rental number string
    """
    if year is None:
        year = datetime.now().year

    # Find the highest sequence number for this year
    pattern = f"R-{year}-%"

    result = await db.execute(
        select(func.count(Rental.id))
        .where(Rental.rental_number.like(pattern))
    )
    count = result.scalar()

    # Next sequence number (001, 002, 003, ...)
    next_sequence = count + 1

    # Format: R-YEAR-SEQUENCE (3 digits)
    rental_number = f"R-{year}-{next_sequence:03d}"

    return rental_number
