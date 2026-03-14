"""
安全与鉴权模块
包含密码哈希和 JWT Token 生成/验证
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from uuid import UUID

from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings


# 密码加密上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # 加密强度
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配

    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码

    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    对密码进行哈希加密

    Args:
        password: 明文密码

    Returns:
        str: 加密后的密码哈希
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT 访问令牌

    Args:
        data: 要编码的数据 (载荷)
        expires_delta: 过期时间增量

    Returns:
        str: JWT Token
    """
    to_encode = data.copy()

    # 计算过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # 添加过期时间到载荷
    to_encode.update({"exp": expire})

    # 编码生成 Token
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """
    解码 JWT Token

    Args:
        token: JWT Token 字符串

    Returns:
        Optional[dict]: 解码后的载荷, 失败返回 None
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
