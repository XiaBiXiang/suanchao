"""
算潮 应用入口
FastAPI 主应用
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import auth, problem, submit, ai, user, discuss, square

# 导入模型以确保它们被注册到 Base
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
from app.models.user import User  # noqa: F401
from app.services.judge_queue import judge_queue_service


# 创建 FastAPI 应用实例
@asynccontextmanager
async def lifespan(app: FastAPI):
    await judge_queue_service.startup()
    try:
        yield
    finally:
        await judge_queue_service.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    description="算潮 在线编程训练平台 API",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# 配置 CORS 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(auth.router)
app.include_router(problem.router)
app.include_router(submit.router)
app.include_router(ai.router)
app.include_router(user.router)
app.include_router(discuss.router)
app.include_router(square.router)


@app.get("/")
async def root():
    """
    根路径健康检查
    """
    return {
        "code": 0,
        "message": "算潮 API is running",
        "data": {"name": settings.APP_NAME, "version": "1.0.0"},
    }


@app.get("/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
