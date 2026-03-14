"""
广场（共享题库）接口
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.problem import (
    Problem,
    ProblemSourceEnum,
    SharedProblem,
    SharedProblemStar,
    SharedProblemImport,
    Submission,
    TestCase,
)
from app.models.user import User
from app.schemas.response import api_response


router = APIRouter(prefix="/api/square", tags=["广场"])


def _difficulty_text(value) -> str:
    if hasattr(value, "value"):
        return value.value
    return str(value)


@router.post("/problems/{problem_id}/share", response_model=dict)
async def share_problem_to_square(
    problem_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    将当前用户的 AI 私有题分享到广场

    规则:
    - 仅支持分享自己的 AI 私有题
    - 必须先 AC 通过至少一次
    - 同一题仅允许分享一次
    """
    problem_result = await db.execute(
        select(Problem).where(
            and_(
                Problem.id == problem_id,
                Problem.source_type == ProblemSourceEnum.AI_GENERATED,
                Problem.owner_id == current_user.id,
            )
        )
    )
    problem = problem_result.scalar_one_or_none()
    if not problem:
        return api_response(code=404, message="仅可分享你自己的 AI 私有题")

    ac_result = await db.execute(
        select(Submission.id).where(
            and_(
                Submission.user_id == current_user.id,
                Submission.problem_id == problem.id,
                Submission.status == "AC",
                Submission.run_mode == "submit",
            )
        ).limit(1)
    )
    passed_once = ac_result.scalar_one_or_none() is not None
    if not passed_once:
        return api_response(code=400, message="请先通过该题后再分享")

    shared_result = await db.execute(
        select(SharedProblem).where(SharedProblem.problem_id == problem.id)
    )
    existed = shared_result.scalar_one_or_none()
    if existed:
        return api_response(
            data={
                "shared_id": str(existed.id),
                "problem_id": str(problem.id),
            },
            message="该题已分享至广场",
            code=0,
        )

    shared = SharedProblem(
        problem_id=problem.id,
        owner_id=current_user.id,
        import_count=0,
    )
    db.add(shared)
    await db.commit()
    await db.refresh(shared)

    return api_response(
        data={
            "shared_id": str(shared.id),
            "problem_id": str(problem.id),
        },
        message="已分享到广场",
        code=0,
    )


@router.get("/problems", response_model=dict)
async def list_square_problems(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    difficulty: Optional[str] = Query(None, description="难度筛选"),
    scope: str = Query("square", description="范围: square|mine"),
    sort_by: str = Query("stars", description="排序: stars|latest"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    获取广场题目列表
    """
    scope_value = (scope or "square").lower()
    if scope_value not in {"square", "mine"}:
        return api_response(code=400, message="scope 仅支持 square 或 mine")
    sort_value = (sort_by or "stars").lower()
    if sort_value not in {"stars", "latest"}:
        return api_response(code=400, message="sort_by 仅支持 stars 或 latest")

    base_conditions = [Problem.source_type == ProblemSourceEnum.AI_GENERATED]
    if difficulty:
        base_conditions.append(Problem.difficulty == difficulty)
    if scope_value == "mine":
        base_conditions.append(SharedProblem.owner_id == current_user.id)
    else:
        base_conditions.append(SharedProblem.owner_id != current_user.id)

    total_result = await db.execute(
        select(func.count(SharedProblem.id))
        .select_from(SharedProblem)
        .join(Problem, Problem.id == SharedProblem.problem_id)
        .where(and_(*base_conditions))
    )
    total = total_result.scalar() or 0
    offset = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    order_fields = (
        [desc(SharedProblem.star_count), desc(SharedProblem.created_at)]
        if sort_value == "stars"
        else [desc(SharedProblem.created_at), desc(SharedProblem.star_count)]
    )

    result = await db.execute(
        select(SharedProblem, Problem, User)
        .join(Problem, Problem.id == SharedProblem.problem_id)
        .join(User, User.id == SharedProblem.owner_id)
        .where(and_(*base_conditions))
        .order_by(*order_fields)
        .offset(offset)
        .limit(page_size)
    )
    rows = result.all()

    shared_ids = [shared.id for shared, _, _ in rows]
    import_map: dict[str, str] = {}
    starred_map: dict[str, bool] = {}
    if shared_ids:
        imports_result = await db.execute(
            select(
                SharedProblemImport.shared_problem_id,
                SharedProblemImport.imported_problem_id,
            ).where(
                and_(
                    SharedProblemImport.user_id == current_user.id,
                    SharedProblemImport.shared_problem_id.in_(shared_ids),
                )
            )
        )
        import_map = {
            str(shared_problem_id): str(imported_problem_id)
            for shared_problem_id, imported_problem_id in imports_result.all()
        }

        stars_result = await db.execute(
            select(SharedProblemStar.shared_problem_id).where(
                and_(
                    SharedProblemStar.user_id == current_user.id,
                    SharedProblemStar.shared_problem_id.in_(shared_ids),
                )
            )
        )
        starred_map = {str(shared_problem_id): True for shared_problem_id in stars_result.scalars().all()}

    items = []
    for shared, problem, owner in rows:
        shared_id = str(shared.id)
        imported_problem_id = import_map.get(shared_id)
        is_owner = str(owner.id) == str(current_user.id)
        items.append(
            {
                "id": shared_id,
                "problem_id": str(problem.id),
                "title": problem.title,
                "difficulty": _difficulty_text(problem.difficulty),
                "owner_id": str(owner.id),
                "owner_username": owner.username,
                "import_count": shared.import_count or 0,
                "star_count": shared.star_count or 0,
                "created_at": shared.created_at.isoformat()
                if isinstance(shared.created_at, datetime)
                else str(shared.created_at),
                "description_preview": (problem.description or "")[:220],
                "is_owner": is_owner,
                "is_starred": bool(starred_map.get(shared_id)),
                "is_imported": imported_problem_id is not None,
                "imported_problem_id": imported_problem_id,
                "can_import": (not is_owner) and imported_problem_id is None,
            }
        )

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


@router.post("/shared/{shared_id}/star", response_model=dict)
async def star_square_problem(
    shared_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Star 广场题目（同一账号对同一分享仅可 Star 一次）
    """
    shared_result = await db.execute(
        select(SharedProblem).where(SharedProblem.id == shared_id)
    )
    shared = shared_result.scalar_one_or_none()
    if not shared:
        return api_response(code=404, message="广场题目不存在")

    existed_result = await db.execute(
        select(SharedProblemStar).where(
            and_(
                SharedProblemStar.shared_problem_id == shared.id,
                SharedProblemStar.user_id == current_user.id,
            )
        )
    )
    existed = existed_result.scalar_one_or_none()
    if existed:
        return api_response(
            data={
                "shared_id": str(shared.id),
                "star_count": shared.star_count or 0,
            },
            message="你已 Star 过该题",
            code=0,
        )

    star_record = SharedProblemStar(
        shared_problem_id=shared.id,
        user_id=current_user.id,
    )
    db.add(star_record)
    shared.star_count = (shared.star_count or 0) + 1
    await db.commit()

    return api_response(
        data={
            "shared_id": str(shared.id),
            "star_count": shared.star_count or 0,
        },
        message="Star 成功",
        code=0,
    )


@router.delete("/shared/{shared_id}", response_model=dict)
async def unshare_square_problem(
    shared_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    取消分享（仅分享者本人）
    """
    shared_result = await db.execute(
        select(SharedProblem).where(SharedProblem.id == shared_id)
    )
    shared = shared_result.scalar_one_or_none()
    if not shared:
        return api_response(code=404, message="分享记录不存在")

    if str(shared.owner_id) != str(current_user.id):
        return api_response(code=403, message="仅可取消自己发布的分享")

    await db.delete(shared)
    await db.commit()
    return api_response(message="已取消分享", code=0)


@router.post("/shared/{shared_id}/import", response_model=dict)
async def import_square_problem(
    shared_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    将广场题目导入当前用户题库（AI 私有）
    """
    shared_result = await db.execute(
        select(SharedProblem, Problem, User)
        .join(Problem, Problem.id == SharedProblem.problem_id)
        .join(User, User.id == SharedProblem.owner_id)
        .where(SharedProblem.id == shared_id)
    )
    row = shared_result.one_or_none()
    if not row:
        return api_response(code=404, message="广场题目不存在")

    shared, problem, owner = row
    if str(owner.id) == str(current_user.id):
        return api_response(code=400, message="不能导入自己分享的题目")

    existed_import_result = await db.execute(
        select(SharedProblemImport).where(
            and_(
                SharedProblemImport.shared_problem_id == shared.id,
                SharedProblemImport.user_id == current_user.id,
            )
        )
    )
    existed_import = existed_import_result.scalar_one_or_none()
    if existed_import:
        return api_response(
            data={
                "shared_id": str(shared.id),
                "imported_problem_id": str(existed_import.imported_problem_id),
            },
            message="你已导入过该题",
            code=0,
        )

    cloned_problem = Problem(
        title=f"【广场】{problem.title}",
        description=(problem.description or "")
        + f"\n\n---\n> 来源：广场分享（分享者：{owner.username}）",
        difficulty=problem.difficulty,
        time_limit=problem.time_limit,
        memory_limit=problem.memory_limit,
        source_type=ProblemSourceEnum.AI_GENERATED,
        owner_id=current_user.id,
        is_square_imported=True,
    )
    db.add(cloned_problem)
    await db.flush()

    cases_result = await db.execute(select(TestCase).where(TestCase.problem_id == problem.id))
    cases = cases_result.scalars().all()
    for case in cases:
        db.add(
            TestCase(
                problem_id=cloned_problem.id,
                input_data=case.input_data,
                expected_output=case.expected_output,
                is_hidden=case.is_hidden,
            )
        )

    import_record = SharedProblemImport(
        shared_problem_id=shared.id,
        user_id=current_user.id,
        imported_problem_id=cloned_problem.id,
    )
    db.add(import_record)
    shared.import_count = (shared.import_count or 0) + 1

    await db.commit()

    return api_response(
        data={
            "shared_id": str(shared.id),
            "imported_problem_id": str(cloned_problem.id),
            "title": cloned_problem.title,
        },
        message="导入成功，已加入你的 AI 私有题库",
        code=0,
    )
