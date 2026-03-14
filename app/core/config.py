"""
应用核心配置模块
使用 pydantic-settings 管理环境变量
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    应用配置类
    从 .env 文件或环境变量加载配置
    """

    # 数据库配置 (PostgreSQL 异步连接 URL)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/suanchao"

    # JWT 安全配置
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 应用配置
    APP_NAME: str = "算潮"
    DEBUG: bool = True

    # OpenAI API 配置 (用于 AI 导师功能 - DeepSeek)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.deepseek.com"
    OPENAI_MODEL: str = "deepseek-chat"
    OPENAI_REQUEST_TIMEOUT_SECONDS: int = 25
    AI_GENERATE_TIMEOUT_SECONDS: int = 18

    # SMTP 邮件配置 (用于发送验证码)
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "算潮"
    SMTP_TIMEOUT_SECONDS: int = 10

    # Redis 配置 (用于验证码存储，未配置则回退内存)
    REDIS_URL: Optional[str] = ""
    REDIS_CONNECT_TIMEOUT_SECONDS: float = 1.5
    REDIS_SOCKET_TIMEOUT_SECONDS: float = 1.5

    # Pydantic Settings 配置
    model_config = SettingsConfigDict(
        env_file=".env",  # 从 .env 文件加载
        env_file_encoding="utf-8",
        case_sensitive=True,  # 区分大小写
        extra="ignore",  # 忽略额外字段
    )


# 创建全局配置实例
settings = Settings()
