"""
用户相关 API 接口
"""

import asyncio

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, delete, select

from app.core.config import settings
from app.core.email import send_verification_code, verify_code
from app.db.session import get_db
from app.models.problem import Problem, ProblemSourceEnum
from app.models.user import User
from app.schemas.response import api_response
from app.api.endpoints.auth import get_current_user


router = APIRouter(prefix="/api/user", tags=["用户"])


class ProfileUpdateRequest(BaseModel):
    username: str


class PasswordUpdateRequest(BaseModel):
    old_password: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    verification_code: str


@router.put("/profile", response_model=dict)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    更新用户资料
    """
    if not profile_data.username or len(profile_data.username) < 3:
        return api_response(code=400, message="用户名至少需要3个字符")

    # 检查用户名是否已被占用
    result = await db.execute(
        select(User).where(
            User.username == profile_data.username, User.id != current_user.id
        )
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        return api_response(code=400, message="用户名已被占用")

    current_user.username = profile_data.username
    await db.commit()
    await db.refresh(current_user)

    return api_response(
        data={
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
        },
        message="更新成功",
        code=0,
    )


@router.put("/password", response_model=dict)
async def update_password(
    password_data: PasswordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    修改密码
    """
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # 验证当前密码
    if not pwd_context.verify(password_data.old_password, current_user.hashed_password):
        return api_response(code=400, message="当前密码错误")

    # 验证新密码长度
    if len(password_data.new_password) < 8:
        return api_response(code=400, message="新密码至少需要8个字符")

    # 更新密码
    current_user.hashed_password = pwd_context.hash(password_data.new_password)
    await db.commit()

    return api_response(message="密码修改成功", code=0)


@router.post("/send-delete-code", response_model=dict)
async def send_delete_code(
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    发送账号注销验证码
    """
    from app.core.email import code_store

    success = await asyncio.to_thread(
        send_verification_code,
        current_user.email,
        "delete_account",
    )
    real_code = (
        await asyncio.to_thread(code_store.get_code, current_user.email, "delete_account")
        if success
        else None
    )

    if success:
        return api_response(
            message="注销验证码已发送到您的邮箱",
            code=0,
            data={"code": real_code} if settings.DEBUG else None,
        )
    return api_response(code=500, message="发送失败，请稍后重试")


@router.delete("/account", response_model=dict)
async def delete_account(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    注销账号（邮箱验证码确认）
    """
    code = (request.verification_code or "").strip()
    if len(code) != 6 or not code.isdigit():
        return api_response(code=400, message="验证码格式不正确")

    is_valid_code = await asyncio.to_thread(
        verify_code,
        current_user.email,
        code,
        "delete_account",
    )
    if not is_valid_code:
        return api_response(code=400, message="验证码错误或已过期")

    user_result = await db.execute(select(User).where(User.id == current_user.id))
    user_to_delete = user_result.scalar_one_or_none()
    if not user_to_delete:
        return api_response(code=404, message="用户不存在")

    # 删除用户名下 AI 私有题，避免 owner 置空后产生不可见孤儿数据
    await db.execute(
        delete(Problem).where(
            and_(
                Problem.source_type == ProblemSourceEnum.AI_GENERATED,
                Problem.owner_id == current_user.id,
            )
        )
    )

    await db.delete(user_to_delete)
    await db.commit()

    return api_response(message="账号已注销", code=0)
