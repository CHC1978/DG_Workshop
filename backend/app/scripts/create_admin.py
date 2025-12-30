"""Create initial admin user"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


async def create_admin_user():
    """Create initial admin user if not exists"""
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("Admin user already exists")
            return

        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="System Administrator",
            hashed_password=hash_password("admin123"),  # Change this password!
            role=UserRole.ADMIN,
            totp_enabled=False,
            is_active=True,
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        print(f"Admin user created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"IMPORTANT: Please change the password after first login!")
        print(f"IMPORTANT: Set up 2FA for security!")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
