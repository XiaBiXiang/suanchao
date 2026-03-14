"""
异步判题队列服务（Redis + Worker）
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.problem import JudgeJob, Problem, Submission, TestCase, WrongProblemNote
from app.services.judge import JudgeResult, run_code_in_sandbox, run_custom_input_in_sandbox

try:
    import redis.asyncio as redis_async
except Exception:  # pragma: no cover - redis 可选
    redis_async = None


logger = logging.getLogger(__name__)


class JudgeQueueService:
    QUEUE_KEY = "suanchao:judge_queue"

    def __init__(self) -> None:
        self._redis = None
        self._local_queue: asyncio.Queue[str] = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

    async def startup(self) -> None:
        await self._connect_redis()
        self._running = True
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker_loop())
            logger.info("Judge worker started")

    async def shutdown(self) -> None:
        self._running = False
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        self._worker_task = None

        if self._redis is not None:
            close_method = getattr(self._redis, "aclose", None)
            if callable(close_method):
                await close_method()
            else:  # pragma: no cover - 兼容旧版 redis
                await self._redis.close()
            self._redis = None
        logger.info("Judge worker stopped")

    async def enqueue_job(self, job_id: str) -> int:
        """
        入队并返回当前排队长度（用于计算位置）。
        """
        if self._redis is not None:
            await self._redis.rpush(self.QUEUE_KEY, job_id)
            queue_size = await self._redis.llen(self.QUEUE_KEY)
            return int(queue_size or 0)

        await self._local_queue.put(job_id)
        return self._local_queue.qsize()

    async def _connect_redis(self) -> None:
        redis_url = (settings.REDIS_URL or "").strip()
        if not redis_url or redis_async is None:
            logger.warning("REDIS_URL 未配置或 redis 依赖不可用，判题队列回退本地内存队列")
            self._redis = None
            return

        try:
            client = redis_async.Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT_SECONDS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
            )
            await client.ping()
            self._redis = client
            logger.info("Judge queue connected to Redis")
        except Exception as exc:  # pragma: no cover - 依赖运行环境
            logger.exception("Redis 连接失败，判题队列回退本地内存队列: %s", exc)
            self._redis = None

    async def _dequeue_job(self) -> Optional[str]:
        if self._redis is not None:
            item = await self._redis.blpop(self.QUEUE_KEY, timeout=3)
            if not item:
                return None
            _, job_id = item
            return str(job_id)

        try:
            return await asyncio.wait_for(self._local_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None

    async def _worker_loop(self) -> None:
        while self._running:
            try:
                job_id = await self._dequeue_job()
                if not job_id:
                    continue
                await self.process_job(job_id)
            except asyncio.CancelledError:
                break
            except Exception as exc:  # pragma: no cover - 防御性
                logger.exception("Judge worker loop error: %s", exc)
                await asyncio.sleep(0.5)

    async def process_job(self, job_id: str) -> None:
        """
        执行单个判题任务。
        """
        async with AsyncSessionLocal() as db:
            job = await db.get(JudgeJob, job_id)
            if not job:
                return
            if job.status not in {"queued", "running"}:
                return
            job.status = "running"
            job.started_at = job.started_at or datetime.utcnow()
            job.progress = max(5, job.progress or 0)
            job.message = "任务开始执行"
            await db.commit()

        try:
            async with AsyncSessionLocal() as db:
                job = await db.get(JudgeJob, job_id)
                if not job:
                    return

                problem = await db.get(Problem, job.problem_id)
                if not problem:
                    raise ValueError("题目不存在")

                async def on_progress(progress: int, message: str) -> None:
                    await self._update_job_progress(job_id, progress, message)

                if job.run_mode == "run":
                    result = await run_custom_input_in_sandbox(
                        code=job.code,
                        custom_input=job.custom_input or "",
                        time_limit_ms=problem.time_limit,
                        memory_limit_mb=problem.memory_limit,
                        language=job.language,
                        progress_callback=on_progress,
                    )
                else:
                    tc_result = await db.execute(
                        select(TestCase).where(TestCase.problem_id == job.problem_id)
                    )
                    test_cases = tc_result.scalars().all()
                    if not test_cases:
                        raise ValueError("该题目没有测试用例")
                    test_case_list = [
                        {
                            "id": str(tc.id),
                            "input_data": tc.input_data,
                            "expected_output": tc.expected_output,
                        }
                        for tc in test_cases
                    ]

                    result = await run_code_in_sandbox(
                        code=job.code,
                        test_cases=test_case_list,
                        time_limit_ms=problem.time_limit,
                        memory_limit_mb=problem.memory_limit,
                        language=job.language,
                        progress_callback=on_progress,
                    )

            await self._complete_job(job_id, result)
        except Exception as exc:
            logger.exception("Judge job failed: %s", exc)
            await self._fail_job(job_id, str(exc))

    async def _update_job_progress(self, job_id: str, progress: int, message: str) -> None:
        async with AsyncSessionLocal() as db:
            job = await db.get(JudgeJob, job_id)
            if not job or job.status != "running":
                return
            next_progress = max(job.progress or 0, max(0, min(100, int(progress))))
            job.progress = next_progress
            job.message = message
            await db.commit()

    def _serialize_result(self, result: JudgeResult) -> dict:
        return {
            "status": result.status,
            "total_cases": result.total_cases,
            "passed_cases": result.passed_cases,
            "total_time_ms": result.total_time_ms,
            "max_memory_mb": result.max_memory_mb,
            "message": result.message,
            "test_results": [
                {
                    "test_case_id": item.test_case_id,
                    "status": item.status,
                    "input_data": item.input_data,
                    "expected_output": item.expected_output,
                    "actual_output": item.actual_output,
                    "execution_time_ms": item.execution_time_ms,
                    "memory_used_mb": item.memory_used_mb,
                    "error_message": item.error_message,
                }
                for item in result.test_results
            ],
        }

    def _next_review_days(self, wrong_count: int) -> int:
        intervals = [1, 2, 4, 7, 14, 30]
        index = max(0, min(len(intervals) - 1, wrong_count - 1))
        return intervals[index]

    async def _update_wrong_note(
        self,
        db,
        user_id,
        problem: Problem,
        result_status: str,
    ) -> None:
        now = datetime.utcnow()
        note_result = await db.execute(
            select(WrongProblemNote).where(
                and_(
                    WrongProblemNote.user_id == user_id,
                    WrongProblemNote.problem_id == problem.id,
                )
            )
        )
        note = note_result.scalar_one_or_none()

        if result_status == "AC":
            if note:
                note.is_resolved = True
                note.next_review_at = None
                note.updated_at = now
            return

        tags = problem.knowledge_tags or []
        if note is None:
            note = WrongProblemNote(
                user_id=user_id,
                problem_id=problem.id,
                wrong_count=1,
                review_count=0,
                is_resolved=False,
                knowledge_tags=tags,
                last_wrong_at=now,
                next_review_at=now + timedelta(days=self._next_review_days(1)),
                created_at=now,
                updated_at=now,
            )
            db.add(note)
            return

        note.wrong_count = (note.wrong_count or 0) + 1
        note.is_resolved = False
        note.knowledge_tags = tags
        note.last_wrong_at = now
        note.next_review_at = now + timedelta(days=self._next_review_days(note.wrong_count))
        note.updated_at = now

    async def _complete_job(self, job_id: str, result: JudgeResult) -> None:
        async with AsyncSessionLocal() as db:
            job = await db.get(JudgeJob, job_id)
            if not job:
                return

            payload = self._serialize_result(result)
            submission = Submission(
                user_id=job.user_id,
                problem_id=job.problem_id,
                code=job.code,
                language=job.language,
                status=result.status,
                passed_cases=result.passed_cases,
                total_cases=result.total_cases,
                run_mode=job.run_mode,
                custom_input=job.custom_input,
                total_time_ms=result.total_time_ms,
                max_memory_mb=result.max_memory_mb,
                result_data=payload,
            )
            db.add(submission)
            await db.flush()

            payload["submission_id"] = str(submission.id)
            job.status = "completed"
            job.progress = 100
            job.message = result.message
            job.error_message = None
            job.result_data = payload
            job.finished_at = datetime.utcnow()

            if job.run_mode == "submit":
                problem = await db.get(Problem, job.problem_id)
                if problem is not None:
                    await self._update_wrong_note(
                        db=db,
                        user_id=job.user_id,
                        problem=problem,
                        result_status=result.status,
                    )

            await db.commit()

    async def _fail_job(self, job_id: str, error_message: str) -> None:
        async with AsyncSessionLocal() as db:
            job = await db.get(JudgeJob, job_id)
            if not job:
                return
            job.status = "failed"
            job.progress = 100
            job.message = "任务执行失败"
            job.error_message = error_message
            job.finished_at = datetime.utcnow()
            await db.commit()


judge_queue_service = JudgeQueueService()
