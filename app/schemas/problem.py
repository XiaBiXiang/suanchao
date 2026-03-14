"""
题目 Pydantic Schema
使用 Pydantic V2 定义请求/响应模型
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class TestCaseBase(BaseModel):
    """
    测试用例基础 Schema
    """

    input_data: str = Field(..., description="输入数据")
    expected_output: str = Field(..., description="期望输出")
    is_hidden: bool = Field(default=False, description="是否隐藏")


class TestCaseCreate(TestCaseBase):
    """
    创建测试用例请求 Schema
    """

    pass


class TestCaseOut(TestCaseBase):
    """
    测试用例输出 Schema
    """

    id: str = Field(..., description="测试用例ID")
    problem_id: str = Field(..., description="关联题目ID")

    model_config = {"from_attributes": True}


class TestCaseOutPublic(TestCaseBase):
    """
    公开测试用例输出 Schema (不包含隐藏用例)
    """

    id: str = Field(..., description="测试用例ID")

    model_config = {"from_attributes": True}


class ProblemBase(BaseModel):
    """
    题目基础 Schema
    """

    title: str = Field(..., min_length=1, max_length=255, description="题目标题")
    description: str = Field(default="", description="题目描述 (支持 Markdown)")
    difficulty: str = Field(default="Easy", description="难度等级")
    time_limit: int = Field(
        default=1000, ge=100, le=10000, description="时间限制 (毫秒)"
    )
    memory_limit: int = Field(default=128, ge=16, le=1024, description="内存限制 (MB)")


class ProblemCreate(ProblemBase):
    """
    创建题目请求 Schema
    """

    pass


class ProblemUpdate(BaseModel):
    """
    更新题目请求 Schema (所有字段可选)
    """

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="题目标题"
    )
    description: Optional[str] = Field(None, description="题目描述")
    difficulty: Optional[str] = Field(None, description="难度等级")
    time_limit: Optional[int] = Field(None, ge=100, le=10000, description="时间限制")
    memory_limit: Optional[int] = Field(None, ge=16, le=1024, description="内存限制")


class ProblemListOut(BaseModel):
    """
    题目列表输出 Schema (简化版)
    """

    id: str = Field(..., description="题目ID")
    title: str = Field(..., description="题目标题")
    difficulty: str = Field(..., description="难度等级")
    source_type: str = Field(default="official", description="题目来源类型")
    is_personal: bool = Field(default=False, description="是否为当前用户私有题")
    is_passed: bool = Field(default=False, description="当前用户是否已通过该题")
    is_shared: bool = Field(default=False, description="当前用户 AI 私有题是否已分享到广场")
    is_square_imported: bool = Field(default=False, description="是否为广场导入题")

    model_config = {"from_attributes": True}


class ProblemOut(BaseModel):
    """
    题目详情输出 Schema (不含测试用例)
    """

    id: str = Field(..., description="题目ID")
    title: str = Field(..., description="题目标题")
    description: str = Field(..., description="题目描述")
    difficulty: str = Field(..., description="难度等级")
    time_limit: int = Field(..., description="时间限制 (毫秒)")
    memory_limit: int = Field(..., description="内存限制 (MB)")
    created_at: datetime = Field(..., description="创建时间")

    model_config = {"from_attributes": True}


class TestCaseForDetail(BaseModel):
    """
    题目详情中包含的测试用例 (公开用例)
    """

    id: str = Field(..., description="测试用例ID")
    input_data: str = Field(..., description="输入数据")
    expected_output: str = Field(..., description="期望输出")
    is_hidden: bool = Field(..., description="是否隐藏")

    model_config = {"from_attributes": True}


class ProblemDetailOut(BaseModel):
    """
    题目详情输出 Schema (包含公开测试用例)
    """

    id: str = Field(..., description="题目ID")
    title: str = Field(..., description="题目标题")
    description: str = Field(..., description="题目描述")
    difficulty: str = Field(..., description="难度等级")
    time_limit: int = Field(..., description="时间限制 (毫秒)")
    memory_limit: int = Field(..., description="内存限制 (MB)")
    created_at: datetime = Field(..., description="创建时间")
    source_type: str = Field(default="official", description="题目来源类型")
    is_personal: bool = Field(default=False, description="是否为当前用户私有题")
    is_square_imported: bool = Field(default=False, description="是否为广场导入题")
    test_cases: List[TestCaseForDetail] = Field(
        default_factory=list, description="公开测试用例"
    )

    model_config = {"from_attributes": True}


class PaginatedProblemList(BaseModel):
    """
    分页题目列表响应
    """

    items: List[ProblemListOut] = Field(..., description="题目列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
