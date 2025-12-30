"""資料庫連線與 Session 管理"""
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# 建立 async engine
# 使用 StaticPool 和 check_same_thread=False 以支援 SQLite async
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 建立 async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 建立 Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    取得資料庫 session
    用於 FastAPI 依賴注入
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """初始化資料庫（建立所有表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # 啟用 SQLite WAL 模式
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA synchronous=NORMAL"))
        await conn.execute(text("PRAGMA cache_size=1000000000"))
        await conn.execute(text("PRAGMA temp_store=memory"))


async def close_db() -> None:
    """關閉資料庫連線"""
    await engine.dispose()
