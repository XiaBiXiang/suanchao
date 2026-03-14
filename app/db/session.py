"""
数据库会话配置模块
使用 SQLAlchemy 2.0 异步驱动 (asyncpg)
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.core.config import settings


# 创建异步引擎
# echo=True 会打印 SQL 语句，用于调试
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # 连接前先测试连接是否有效
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 允许超出的连接数
)


# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不自动过期对象
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    声明式基类
    所有模型类都需要继承此类
    """

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖注入用的数据库会话生成器

    用法:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: 异步数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # 自动提交
        except Exception:
            await session.rollback()  # 自动回滚
            raise
        finally:
            await session.close()
