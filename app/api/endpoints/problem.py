"""
题目路由接口
包含题目列表、详情、创建、测试用例管理
"""

import math
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.api.problem_access import (
    get_visible_problem,
    is_personal_problem,
    source_type_value,
    visible_problem_condition,
)
from app.db.session import get_db
from app.models.problem import (
    Problem,
    ProblemSourceEnum,
    Submission,
    TestCase,
    WrongProblemNote,
)
from app.models.problem import SharedProblem
from app.models.user import User
from app.schemas.problem import (
    ProblemCreate,
    ProblemDetailOut,
    ProblemListOut,
    TestCaseCreate,
    TestCaseForDetail,
)
from app.schemas.response import api_response


router = APIRouter(prefix="/api/problems", tags=["题目"])


def _next_review_interval_days(review_count: int) -> int:
    intervals = [2, 4, 7, 14, 30]
    index = max(0, min(len(intervals) - 1, review_count - 1))
    return intervals[index]


@router.get("", response_model=dict)
async def get_problems(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    获取当前用户可见的题目列表 (分页)

    可见性规则:
    - 官方题: 全员可见
    - AI 题: 仅题目 owner 可见
    """
    conditions = [visible_problem_condition(current_user.id)]
    if difficulty:
        conditions.append(Problem.difficulty == difficulty)

    total_result = await db.execute(
        select(func.count(Problem.id)).where(and_(*conditions))
    )
    total = total_result.scalar() or 0

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size

    result = await db.execute(
        select(Problem)
        .where(and_(*conditions))
        .order_by(Problem.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    problems = result.scalars().all()
    problem_ids = [problem.id for problem in problems]

    passed_problem_ids: set[str] = set()
    if problem_ids:
        passed_result = await db.execute(
            select(distinct(Submission.problem_id)).where(
                and_(
                    Submission.user_id == current_user.id,
                    Submission.status == "AC",
                    Submission.run_mode == "submit",
                    Submission.problem_id.in_(problem_ids),
                )
            )
        )
        passed_problem_ids = {str(problem_id) for problem_id in passed_result.scalars().all()}

    shared_problem_ids: set[str] = set()
    if problem_ids:
        shared_result = await db.execute(
            select(SharedProblem.problem_id).where(
                and_(
                    SharedProblem.owner_id == current_user.id,
                    SharedProblem.problem_id.in_(problem_ids),
                )
            )
        )
        shared_problem_ids = {str(problem_id) for problem_id in shared_result.scalars().all()}

    items = [
        ProblemListOut(
            id=str(problem.id),
            title=problem.title,
            difficulty=problem.difficulty.value
            if hasattr(problem.difficulty, "value")
            else problem.difficulty,
            source_type=source_type_value(problem),
            is_personal=is_personal_problem(problem, current_user.id),
            is_passed=str(problem.id) in passed_problem_ids,
            is_shared=str(problem.id) in shared_problem_ids,
            is_square_imported=bool(problem.is_square_imported),
        )
        for problem in problems
    ]

    return api_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
        message="获取成功",
        code=0,
    )


@router.get("/stats", response_model=dict)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    获取用户刷题统计（仅统计官方题库题）
    """
    official_condition = or_(
        Problem.source_type == ProblemSourceEnum.OFFICIAL,
        Problem.source_type.is_(None),
    )

    total_problems_result = await db.execute(
        select(func.count(Problem.id)).where(official_condition)
    )
    total_problems = total_problems_result.scalar() or 0

    passed_problems_result = await db.execute(
        select(func.count(distinct(Submission.problem_id)))
        .join(Problem, Problem.id == Submission.problem_id)
        .where(
            and_(
                Submission.user_id == current_user.id,
                Submission.status == "AC",
                Submission.run_mode == "submit",
                official_condition,
            )
        )
    )
    passed_problems = passed_problems_result.scalar() or 0

    completion_rate = (
        round((passed_problems / total_problems * 100), 1) if total_problems > 0 else 0
    )

    return api_response(
        data={
            "total_problems": total_problems,
            "passed_problems": passed_problems,
            "completion_rate": completion_rate,
        },
        message="获取成功",
        code=0,
    )


@router.get("/wrong-book", response_model=dict)
async def list_wrong_book(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tag: Optional[str] = Query(None, description="知识点标签筛选"),
    due_only: bool = Query(False, description="仅看到期复习"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    获取当前用户错题本（支持知识点筛选与二刷提醒）。
    """
    now = datetime.utcnow()
    conditions = [WrongProblemNote.user_id == current_user.id]
    if due_only:
        conditions.append(
            and_(
                WrongProblemNote.is_resolved == False,
                WrongProblemNote.next_review_at.is_not(None),
                WrongProblemNote.next_review_at <= now,
            )
        )

    result = await db.execute(
        select(WrongProblemNote, Problem)
        .join(Problem, Problem.id == WrongProblemNote.problem_id)
        .where(and_(*conditions))
        .order_by(
            WrongProblemNote.next_review_at.asc().nulls_last(),
            WrongProblemNote.updated_at.desc(),
        )
    )
    rows = result.all()
    if tag:
        rows = [row for row in rows if tag in (row[0].knowledge_tags or [])]

    total = len(rows)
    offset = (page - 1) * page_size
    paged_rows = rows[offset : offset + page_size]

    items = []
    for note, problem in paged_rows:
        next_review_at = note.next_review_at
        due = bool(next_review_at and next_review_at <= now and not note.is_resolved)
        items.append(
            {
                "problem_id": str(problem.id),
                "title": problem.title,
                "difficulty": problem.difficulty.value
                if hasattr(problem.difficulty, "value")
                else str(problem.difficulty),
                "knowledge_tags": note.knowledge_tags or [],
                "wrong_count": note.wrong_count,
                "review_count": note.review_count,
                "is_resolved": bool(note.is_resolved),
                "last_wrong_at": note.last_wrong_at.isoformat()
                if note.last_wrong_at
                else None,
                "last_review_at": note.last_review_at.isoformat()
                if note.last_review_at
                else None,
                "next_review_at": next_review_at.isoformat() if next_review_at else None,
                "is_due": due,
            }
        )

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return api_response(
        code=0,
        message="获取成功",
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    )


@router.post("/wrong-book/{problem_id}/reviewed", response_model=dict)
async def mark_wrong_problem_reviewed(
    problem_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    标记错题已复习，推进下一次复习时间。
    """
    result = await db.execute(
        select(WrongProblemNote).where(
            and_(
                WrongProblemNote.user_id == current_user.id,
                WrongProblemNote.problem_id == problem_id,
            )
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        return api_response(code=404, message="错题记录不存在")

    now = datetime.utcnow()
    note.review_count = (note.review_count or 0) + 1
    note.last_review_at = now
    note.updated_at = now

    if note.is_resolved:
        note.next_review_at = None
    else:
        next_days = _next_review_interval_days(note.review_count)
        note.next_review_at = now + timedelta(days=next_days)

    await db.commit()
    return api_response(
        code=0,
        message="已记录复习进度",
        data={
            "problem_id": problem_id,
            "review_count": note.review_count,
            "next_review_at": note.next_review_at.isoformat()
            if note.next_review_at
            else None,
        },
    )


@router.get("/{problem_id}", response_model=dict)
async def get_problem_detail(
    problem_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    获取题目详情 (包含公开测试用例)
    """
    problem = await get_visible_problem(
        db=db,
        problem_id=problem_id,
        user_id=current_user.id,
    )
    if not problem:
        return api_response(code=404, message="题目不存在或无权限访问")

    test_result = await db.execute(
        select(TestCase).where(
            and_(TestCase.problem_id == problem_id, TestCase.is_hidden == False)
        )
    )
    test_cases = test_result.scalars().all()

    test_case_list = [
        TestCaseForDetail(
            id=str(test_case.id),
            input_data=test_case.input_data,
            expected_output=test_case.expected_output,
            is_hidden=test_case.is_hidden,
        )
        for test_case in test_cases
    ]

    return api_response(
        data=ProblemDetailOut(
            id=str(problem.id),
            title=problem.title,
            description=problem.description,
            difficulty=problem.difficulty.value
            if hasattr(problem.difficulty, "value")
            else problem.difficulty,
            time_limit=problem.time_limit,
            memory_limit=problem.memory_limit,
            created_at=problem.created_at,
            source_type=source_type_value(problem),
            is_personal=is_personal_problem(problem, current_user.id),
            is_square_imported=bool(problem.is_square_imported),
            test_cases=test_case_list,
        ).model_dump(),
        message="获取成功",
        code=0,
    )


@router.post("", response_model=dict)
async def create_problem(
    problem_data: ProblemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    创建新题目（默认官方题）
    """
    new_problem = Problem(
        title=problem_data.title,
        description=problem_data.description,
        difficulty=problem_data.difficulty,
        time_limit=problem_data.time_limit,
        memory_limit=problem_data.memory_limit,
        source_type=ProblemSourceEnum.OFFICIAL,
        owner_id=None,
    )

    db.add(new_problem)
    await db.commit()
    await db.refresh(new_problem)

    return api_response(
        data={
            "id": str(new_problem.id),
            "title": new_problem.title,
            "difficulty": new_problem.difficulty.value
            if hasattr(new_problem.difficulty, "value")
            else new_problem.difficulty,
            "time_limit": new_problem.time_limit,
            "memory_limit": new_problem.memory_limit,
            "source_type": source_type_value(new_problem),
            "is_personal": False,
        },
        message="创建成功",
        code=0,
    )


@router.post("/{problem_id}/testcases", response_model=dict)
async def add_test_case(
    problem_id: str,
    test_case_data: TestCaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    为指定题目添加测试用例
    """
    problem = await get_visible_problem(
        db=db,
        problem_id=problem_id,
        user_id=current_user.id,
    )
    if not problem:
        return api_response(code=404, message="题目不存在或无权限访问")

    new_test_case = TestCase(
        problem_id=problem_id,
        input_data=test_case_data.input_data,
        expected_output=test_case_data.expected_output,
        is_hidden=test_case_data.is_hidden,
    )

    db.add(new_test_case)
    await db.commit()
    await db.refresh(new_test_case)

    return api_response(
        data={
            "id": str(new_test_case.id),
            "problem_id": str(new_test_case.problem_id),
            "input_data": new_test_case.input_data,
            "expected_output": new_test_case.expected_output,
            "is_hidden": new_test_case.is_hidden,
        },
        message="创建成功",
        code=0,
    )


@router.put("/{problem_id}", response_model=dict)
async def update_problem(
    problem_id: str,
    problem_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    更新题目 (简化版，使用 dict)
    """
    problem = await get_visible_problem(
        db=db,
        problem_id=problem_id,
        user_id=current_user.id,
    )
    if not problem:
        return api_response(code=404, message="题目不存在或无权限访问")

    if "title" in problem_data and problem_data["title"]:
        problem.title = problem_data["title"]
    if "description" in problem_data:
        problem.description = problem_data["description"]
    if "difficulty" in problem_data and problem_data["difficulty"]:
        problem.difficulty = problem_data["difficulty"]
    if "time_limit" in problem_data:
        problem.time_limit = problem_data["time_limit"]
    if "memory_limit" in problem_data:
        problem.memory_limit = problem_data["memory_limit"]

    await db.commit()
    await db.refresh(problem)

    return api_response(
        data={
            "id": str(problem.id),
            "title": problem.title,
            "difficulty": problem.difficulty.value
            if hasattr(problem.difficulty, "value")
            else problem.difficulty,
            "source_type": source_type_value(problem),
            "is_personal": is_personal_problem(problem, current_user.id),
        },
        message="更新成功",
        code=0,
    )


@router.delete("/{problem_id}", response_model=dict)
async def delete_problem(
    problem_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    删除题目

    权限规则:
    - 仅允许删除当前用户的 AI 私有题
    - 官方题与他人私有题不可删除
    """
    problem = await get_visible_problem(
        db=db,
        problem_id=problem_id,
        user_id=current_user.id,
    )
    if not problem:
        return api_response(code=404, message="题目不存在或无权限访问")

    is_ai_private = (
        source_type_value(problem) == ProblemSourceEnum.AI_GENERATED.value
        and str(problem.owner_id) == str(current_user.id)
    )
    if not is_ai_private:
        return api_response(code=403, message="仅可删除你自己的 AI 私有题")

    await db.delete(problem)
    await db.commit()

    return api_response(message="题目已删除", code=0)
