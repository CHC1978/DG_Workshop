"""臨時腳本：禁用用戶的 2FA"""
import asyncio
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.user import User


async def disable_2fa_for_user(username: str):
    """禁用指定用戶的 2FA"""
    async with AsyncSessionLocal() as db:
        # 查詢用戶
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user:
            print(f"❌ 用戶 '{username}' 不存在")
            return

        # 禁用 2FA
        user.totp_enabled = False
        user.totp_secret = None

        await db.commit()

        print(f"✅ 已禁用用戶 '{username}' 的 2FA")
        print(f"   請使用帳號密碼重新登入，然後重新設定 2FA")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("使用方式: python disable_2fa.py <username>")
        print("範例: python disable_2fa.py admin")
        sys.exit(1)

    username = sys.argv[1]
    asyncio.run(disable_2fa_for_user(username))
