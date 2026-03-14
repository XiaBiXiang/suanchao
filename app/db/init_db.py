"""
初始化数据库表
运行此脚本创建所有表
"""

import asyncio
from sqlalchemy import text

from app.db.session import engine, Base
from app.models.user import User
from app.models.problem import (  # noqa: F401
    AiProblemFeedback,
    Comment,
    JudgeJob,
    Post,
    Problem,
    SharedProblem,
    SharedProblemImport,
    SharedProblemStar,
    Submission,
    TestCase,
    WrongProblemNote,
)


async def init_db():
    """
    初始化数据库: 创建所有表
    """
    async with engine.begin() as conn:
        # 删除所有表 (开发环境)
        await conn.run_sync(Base.metadata.drop_all)
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    print("数据库表创建成功!")


if __name__ == "__main__":
    asyncio.run(init_db())
