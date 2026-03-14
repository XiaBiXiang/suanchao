"""
统一 API 响应格式
遵循 RESTful 规范
"""

from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """
    统一响应模型

    字段说明:
        code: 状态码 (0=成功, 其他=失败)
        message: 响应消息
        data: 响应数据 (可选)
    """

    code: int = Field(default=0, description="状态码")
    message: str = Field(default="Success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")

    @classmethod
    def success(cls, data: Any = None, message: str = "Success") -> "ResponseModel":
        """
        成功响应工厂方法
        """
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, message: str, code: int = 400) -> "ResponseModel":
        """
        错误响应工厂方法
        """
        return cls(code=code, message=message, data=None)


def api_response(data: Any = None, message: str = "Success", code: int = 0) -> dict:
    """
    快速创建 API 响应字典

    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码

    Returns:
        dict: 响应字典
    """
    return {"code": code, "message": message, "data": data}
