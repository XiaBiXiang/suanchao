"""
提交判题 API（异步队列版）
"""

from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.api.problem_access import visible_problem_condition
from app.db.session import get_db
from app.models.problem import JudgeJob, Problem, Submission, TestCase
from app.models.user import User
from app.schemas.response import api_response
from app.services.judge_queue import judge_queue_service


router = APIRouter(prefix="/api/submit", tags=["提交判题"])


class SubmitQueueRequest(BaseModel):
    problem_id: str = Field(..., description="题目ID")
    code: str = Field(..., description="用户代码")
    language: str = Field(default="python", description="编程语言")
    run_mode: Literal["run", "submit"] = Field(
        default="submit",
        description="run=自定义输入运行，submit=提交判题",
    )
    custom_input: Optional[str] = Field(
        default=None,
        description="自定义输入（run 模式可用）",
    )


class JudgeJobOut(BaseModel):
    job_id: str
    problem_id: str
    status: str
    progress: int
    queue_position: int
    message: Optional[str] = None
    run_mode: str


def _serialize_datetime(value: datetime | None) -> Optional[str]:
    if value is None:
        return None
    return value.isoformat()


async def _calculate_queue_position(db: AsyncSession, job: JudgeJob) -> int:
    if job.status != "queued":
        return 0
    result = await db.execute(
        select(func.count(JudgeJob.id)).where(
            and_(
                JudgeJob.status == "queued",
                JudgeJob.created_at <= job.created_at,
            )
        )
    )
    return int(result.scalar() or 0)


def _serialize_submission(item: Submission) -> dict:
    return {
        "id": str(item.id),
        "status": item.status,
        "language": item.language,
        "run_mode": item.run_mode,
        "custom_input": item.custom_input,
        "passed_cases": item.passed_cases,
        "total_cases": item.total_cases,
        "total_time_ms": item.total_time_ms,
        "max_memory_mb": item.max_memory_mb,
        "created_at": _serialize_datetime(item.created_at),
        "code": item.code,
        "result_data": item.result_data,
    }


async def _enqueue_job(
    payload: SubmitQueueRequest,
    current_user: User,
    db: AsyncSession,
) -> dict:
    problem_result = await db.execute(
        select(Problem).where(
            and_(
                Problem.id == payload.problem_id,
                visible_problem_condition(current_user.id),
            )
        )
    )
    problem = problem_result.scalar_one_or_none()
    if not problem:
        return api_response(code=404, message="题目不存在或无权限访问")

    if payload.run_mode == "submit":
        test_case_result = await db.execute(
            select(TestCase.id).where(TestCase.problem_id == payload.problem_id).limit(1)
        )
        if test_case_result.scalar_one_or_none() is None:
            return api_response(code=400, message="该题目没有测试用例")

    job = JudgeJob(
        user_id=current_user.id,
        problem_id=payload.problem_id,
        code=payload.code,
        language=payload.language,
        run_mode=payload.run_mode,
        custom_input=payload.custom_input if payload.run_mode == "run" else None,
        status="queued",
        progress=0,
        message="已进入判题队列",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    try:
        await judge_queue_service.enqueue_job(str(job.id))
    except Exception as exc:
        job.status = "failed"
        job.progress = 100
        job.message = "入队失败"
        job.error_message = str(exc)
        job.finished_at = datetime.utcnow()
        await db.commit()
        return api_response(code=500, message="判题队列暂不可用，请稍后重试")

    queue_position = await _calculate_queue_position(db, job)
    return api_response(
        code=0,
        message="已加入判题队列",
        data=JudgeJobOut(
            job_id=str(job.id),
            problem_id=str(job.problem_id),
            status=job.status,
            progress=job.progress,
            queue_position=queue_position,
            message=job.message,
            run_mode=job.run_mode,
        ).model_dump(),
    )


@router.post("", response_model=dict)
async def submit_code(
    submit_data: SubmitQueueRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    兼容旧接口：默认按队列提交。
    """
    return await _enqueue_job(payload=submit_data, current_user=current_user, db=db)


@router.post("/queue", response_model=dict)
async def submit_code_queue(
    submit_data: SubmitQueueRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    显式入队接口。
    """
    return await _enqueue_job(payload=submit_data, current_user=current_user, db=db)


@router.get("/jobs/{job_id}", response_model=dict)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(JudgeJob).where(
            and_(
                JudgeJob.id == job_id,
                JudgeJob.user_id == current_user.id,
            )
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        return api_response(code=404, message="任务不存在")

    queue_position = await _calculate_queue_position(db, job)
    return api_response(
        code=0,
        message="获取成功",
        data={
            "job_id": str(job.id),
            "problem_id": str(job.problem_id),
            "status": job.status,
            "progress": int(job.progress or 0),
            "queue_position": queue_position,
            "run_mode": job.run_mode,
            "message": job.message,
            "error_message": job.error_message,
            "created_at": _serialize_datetime(job.created_at),
            "started_at": _serialize_datetime(job.started_at),
            "finished_at": _serialize_datetime(job.finished_at),
            "result_data": job.result_data,
        },
    )


@router.get("/history/{problem_id}", response_model=dict)
async def get_submit_history(
    problem_id: str,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    visible_problem_result = await db.execute(
        select(Problem.id).where(
            and_(
                Problem.id == problem_id,
                visible_problem_condition(current_user.id),
            )
        )
    )
    if visible_problem_result.scalar_one_or_none() is None:
        return api_response(code=404, message="题目不存在或无权限访问")

    result = await db.execute(
        select(Submission)
        .where(
            and_(
                Submission.user_id == current_user.id,
                Submission.problem_id == problem_id,
            )
        )
        .order_by(Submission.created_at.desc())
        .limit(limit)
    )
    items: List[Submission] = result.scalars().all()
    return api_response(
        code=0,
        message="获取成功",
        data={
            "items": [_serialize_submission(item) for item in items],
            "total": len(items),
        },
    )
