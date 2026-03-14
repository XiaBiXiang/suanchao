"""
认证路由接口
包含注册、登录、获取当前用户功能
"""

import asyncio
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from jose import JWTError, jwt

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.schemas.response import api_response
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.core.config import settings
from app.core.email import send_verification_code, verify_code


# 创建路由
router = APIRouter(prefix="/api/auth", tags=["认证"])

# Bearer Token 安全依赖
security = HTTPBearer(auto_error=False)


# 验证码请求 Schema
class SendCodeRequest(BaseModel):
    email: str = Field(..., description="邮箱地址")


# 注册请求 Schema (需要验证码)
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, description="密码")
    verification_code: str = Field(
        ..., min_length=6, max_length=6, description="验证码"
    )


class ResetPasswordRequest(BaseModel):
    email: str = Field(..., description="邮箱")
    verification_code: str = Field(
        ..., min_length=6, max_length=6, description="重置验证码"
    )
    new_password: str = Field(..., min_length=8, description="新密码")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    token = credentials.credentials

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用"
        )

    return user


@router.post("/send-code", response_model=dict)
async def send_code(
    request: SendCodeRequest,
) -> dict:
    """
    发送邮箱验证码

    Args:
        request: 包含邮箱地址的请求

    Returns:
        dict: 发送结果
    """
    # 检查邮箱格式
    if not request.email or "@" not in request.email:
        return api_response(code=400, message="邮箱格式不正确")

    # 发送验证码
    from app.core.email import code_store

    success = await asyncio.to_thread(
        send_verification_code, request.email, "register"
    )

    # 获取验证码 (开发模式返回)
    real_code = (
        await asyncio.to_thread(code_store.get_code, request.email, "register")
        if success
        else None
    )

    if success:
        return api_response(
            message="验证码已发送到您的邮箱",
            code=0,
            data={"code": real_code} if settings.DEBUG else None,
        )
    else:
        return api_response(code=500, message="发送失败，请稍后重试")


@router.post("/register", response_model=dict)
async def register(
    request: RegisterRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """
    用户注册接口 (需要邮箱验证码)

    1. 验证验证码
    2. 检查用户名/邮箱是否已存在
    3. 加密密码
    4. 创建用户记录

    Args:
        request: 注册请求 (包含验证码)
        db: 数据库会话

    Returns:
        dict: 统一格式的响应
    """
    # 1. 验证验证码
    is_valid_code = await asyncio.to_thread(
        verify_code,
        request.email,
        request.verification_code,
        "register",
    )
    if not is_valid_code:
        return api_response(code=400, message="验证码错误或已过期")

    # 2. 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        return api_response(code=400, message="邮箱已被注册")

    # 3. 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        return api_response(code=400, message="用户名已被使用")

    # 4. 加密密码并创建用户
    hashed_password = get_password_hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        return api_response(code=500, message="注册失败, 请稍后重试")

    return api_response(
        data={
            "id": str(new_user.id),
            "username": new_user.username,
            "email": new_user.email,
        },
        message="注册成功",
        code=0,
    )


@router.post("/send-reset-code", response_model=dict)
async def send_reset_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    发送重置密码验证码
    """
    if not request.email or "@" not in request.email:
        return api_response(code=400, message="邮箱格式不正确")

    user_result = await db.execute(select(User).where(User.email == request.email))
    user = user_result.scalar_one_or_none()
    if not user:
        return api_response(code=404, message="该邮箱未注册")

    from app.core.email import code_store

    success = await asyncio.to_thread(
        send_verification_code, request.email, "reset_password"
    )
    real_code = (
        await asyncio.to_thread(code_store.get_code, request.email, "reset_password")
        if success
        else None
    )

    if success:
        return api_response(
            message="重置验证码已发送到您的邮箱",
            code=0,
            data={"code": real_code} if settings.DEBUG else None,
        )
    return api_response(code=500, message="发送失败，请稍后重试")


@router.post("/reset-password", response_model=dict)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    通过邮箱验证码重置密码
    """
    if not request.email or "@" not in request.email:
        return api_response(code=400, message="邮箱格式不正确")

    user_result = await db.execute(select(User).where(User.email == request.email))
    user = user_result.scalar_one_or_none()
    if not user:
        return api_response(code=404, message="该邮箱未注册")

    is_valid_code = await asyncio.to_thread(
        verify_code,
        request.email,
        request.verification_code,
        "reset_password",
    )
    if not is_valid_code:
        return api_response(code=400, message="验证码错误或已过期")

    if len(request.new_password) < 8:
        return api_response(code=400, message="密码至少 8 位")

    has_letter = any(ch.isalpha() for ch in request.new_password)
    has_digit = any(ch.isdigit() for ch in request.new_password)
    if not has_letter or not has_digit:
        return api_response(code=400, message="密码需包含字母和数字")

    user.hashed_password = get_password_hash(request.new_password)
    await db.commit()

    return api_response(message="密码重置成功，请使用新密码登录", code=0)


@router.post("/login", response_model=dict)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)) -> dict:
    """
    用户登录接口

    1. 根据邮箱查询用户
    2. 验证密码
    3. 生成 JWT Token

    Args:
        login_data: 用户登录数据
        db: 数据库会话

    Returns:
        dict: 包含 Token 的响应
    """
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user:
        return api_response(code=401, message="邮箱或密码错误")

    if not verify_password(login_data.password, user.hashed_password):
        return api_response(code=401, message="邮箱或密码错误")

    if not user.is_active:
        return api_response(code=403, message="账号已被禁用")

    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return api_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
            },
        },
        message="登录成功",
        code=0,
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> dict:
    """
    获取当前用户信息接口

    需要在请求头中携带有效的 Bearer Token

    Args:
        current_user: 当前用户 (通过依赖注入)

    Returns:
        dict: 用户信息
    """
    return api_response(
        data={
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "is_active": current_user.is_active,
            "is_superuser": current_user.is_superuser,
            "created_at": current_user.created_at.isoformat(),
        },
        message="获取成功",
        code=0,
    )
