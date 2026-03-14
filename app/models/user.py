"""
用户数据模型
使用 SQLAlchemy 2.0 异步 ORM
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class User(Base):
    """
    用户表模型

    字段说明:
        id: 主键 UUID
        username: 用户名 (唯一, 必填)
        email: 邮箱 (唯一, 索引, 必填)
        hashed_password: 加密后的密码
        is_active: 是否激活 (用于软删除/禁用)
        is_superuser: 是否超级管理员
        created_at: 创建时间
    """

    __tablename__ = "users"

    # 主键 UUID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="用户唯一标识"
    )

    # 用户名 (唯一)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="用户名"
    )

    # 邮箱 (唯一, 索引)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True, comment="邮箱"
    )

    # 密码哈希
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="加密后的密码"
    )

    # 是否激活
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否激活"
    )

    # 是否超级管理员
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否超级管理员"
    )

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, comment="创建时间"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
