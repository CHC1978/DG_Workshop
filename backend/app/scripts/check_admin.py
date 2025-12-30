"""Check if admin user exists"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User


async def check_admin():
    """Check if admin user exists"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        user = result.scalar_one_or_none()

        if user:
            print(f"✅ Admin user exists")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role.value}")
            print(f"   2FA Enabled: {user.totp_enabled}")
            print(f"   Active: {user.is_active}")
        else:
            print("❌ Admin user not found")


if __name__ == "__main__":
    asyncio.run(check_admin())
