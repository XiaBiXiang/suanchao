"""
题目可见性与来源辅助函数
"""

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problem import Problem, ProblemSourceEnum


def visible_problem_condition(user_id):
    """
    当前用户可见题目条件:
    - 官方题: 全员可见
    - AI 题: 仅 owner 可见
    """
    return or_(
        Problem.source_type == ProblemSourceEnum.OFFICIAL,
        Problem.source_type.is_(None),
        and_(
            Problem.source_type == ProblemSourceEnum.AI_GENERATED,
            Problem.owner_id == user_id,
        ),
    )


def source_type_value(problem: Problem) -> str:
    """
    统一返回字符串来源类型
    """
    source_type = problem.source_type
    if hasattr(source_type, "value"):
        return source_type.value
    if source_type is None:
        return ProblemSourceEnum.OFFICIAL.value
    return str(source_type)


def is_personal_problem(problem: Problem, user_id) -> bool:
    """
    是否为当前用户的 AI 私有题
    """
    return (
        source_type_value(problem) == ProblemSourceEnum.AI_GENERATED.value
        and str(problem.owner_id) == str(user_id)
    )


async def get_visible_problem(
    db: AsyncSession,
    problem_id: str,
    user_id,
) -> Problem | None:
    """
    按可见性查询单题
    """
    result = await db.execute(
        select(Problem).where(
            and_(Problem.id == problem_id, visible_problem_condition(user_id))
        )
    )
    return result.scalar_one_or_none()
