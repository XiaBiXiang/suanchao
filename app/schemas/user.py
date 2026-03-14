"""
用户 Pydantic Schema
使用 Pydantic V2 定义请求/响应模型
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """
    用户注册请求 Schema

    验证规则:
        - username: 3-50字符, 字母数字下划线
        - email: 有效邮箱格式
        - password: 至少8位, 包含字母和数字
    """

    username: str = Field(
        ...,  # 必填
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="用户名",
    )
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=8, description="密码")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        验证密码强度: 必须包含字母和数字
        """
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"[0-9]", v):
            raise ValueError("密码必须包含数字")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        验证用户名格式
        """
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("用户名必须以字母开头")
        return v


class UserLogin(BaseModel):
    """
    用户登录请求 Schema
    """

    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")


class UserOut(BaseModel):
    """
    用户信息输出 Schema (脱敏)
    不包含敏感信息如密码
    """

    id: UUID = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    is_active: bool = Field(..., description="是否激活")
    is_superuser: bool = Field(..., description="是否超级管理员")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """
    JWT Token 响应 Schema
    """

    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    """
    Token 载荷数据 Schema
    """

    user_id: Optional[UUID] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
