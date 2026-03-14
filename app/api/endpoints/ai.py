"""
AI 导师聊天接口
使用 SSE 流式输出
"""

import hashlib
import re
from difflib import SequenceMatcher
from typing import Literal, Optional
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, and_, or_, desc

from app.api.problem_access import visible_problem_condition
from app.db.session import get_db
from app.models.user import User
from app.models.problem import (
    AiProblemFeedback,
    Problem,
    ProblemSourceEnum,
    TestCase,
    Submission,
    DifficultyEnum,
)
from app.services.llm import get_llm_response, generate_ai_problem
from app.api.endpoints.auth import get_current_user
from app.schemas.response import api_response


router = APIRouter(prefix="/api/ai", tags=["AI导师"])

SIMILARITY_TITLE_THRESHOLD = 0.78
SIMILARITY_DESCRIPTION_THRESHOLD = 0.72
MAX_GENERATE_ATTEMPTS = 4
RECENT_AI_PROBLEMS_LIMIT = 80


class ChatRequest(BaseModel):
    """
    AI 聊天请求
    """

    problem_description: str = Field(..., description="题目描述")
    current_code: str = Field(..., description="用户当前代码")
    user_message: str = Field(..., description="用户消息")


class GenerateProblemRequest(BaseModel):
    """
    AI 出题请求
    """

    mode: Literal["progress", "custom", "estimate"] = Field(
        default="progress",
        description=(
            "出题模式：progress=按进度估计，custom=自定义等级，"
            "estimate=旧版兼容（等同 progress）"
        ),
    )
    level: Optional[int] = Field(
        default=None, ge=1, le=10, description="自定义难度等级（1-10）"
    )


class ProblemFeedbackRequest(BaseModel):
    vote: Literal["up", "down"] = Field(..., description="反馈投票")
    reason: Optional[str] = Field(default=None, max_length=500, description="反馈原因")


async def chat_generator(
    problem_description: str,
    current_code: str,
    user_message: str,
) -> str:
    """
    流式响应生成器

    将 LLM 的流式输出转换为 SSE 格式
    """
    async for chunk in get_llm_response(
        problem_description=problem_description,
        current_code=current_code,
        user_message=user_message,
    ):
        # 发送 SSE 格式的数据
        yield f"data: {chunk}\n\n"


@router.post("/chat")
async def chat(
    chat_data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    AI 导师聊天接口

    使用 SSE 流式输出，返回打字机体验

    Args:
        chat_data: 聊天请求数据
        current_user: 当前用户

    Returns:
        StreamingResponse: SSE 流式响应
    """
    return StreamingResponse(
        chat_generator(
            problem_description=chat_data.problem_description,
            current_code=chat_data.current_code,
            user_message=chat_data.user_message,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


def level_to_difficulty(level: int) -> str:
    if level <= 3:
        return "Easy"
    if level <= 7:
        return "Medium"
    return "Hard"


def normalize_text_for_hash(text: str) -> str:
    normalized = " ".join((text or "").strip().lower().split())
    return normalized


def content_hash(text: str) -> str:
    payload = normalize_text_for_hash(text)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_text_for_similarity(text: str, limit: int = 1800) -> str:
    compact = str(text or "").lower()
    compact = re.sub(r"```[\s\S]*?```", " ", compact)
    compact = re.sub(r"[`*_>#\-~]+", " ", compact)
    compact = re.sub(r"\s+", "", compact)
    return compact[:limit]


def text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def summarize_text(text: str, limit: int = 96) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: max(1, limit - 1)] + "…"


def find_similar_problem(
    title: str,
    description: str,
    existing_problems: list[Problem],
) -> Optional[dict]:
    target_title = normalize_text_for_similarity(title, limit=180)
    target_desc = normalize_text_for_similarity(description, limit=1400)
    best: Optional[dict] = None

    for problem in existing_problems:
        existed_title = normalize_text_for_similarity(problem.title or "", limit=180)
        existed_desc = normalize_text_for_similarity(problem.description or "", limit=1400)
        title_ratio = text_similarity(target_title, existed_title)
        desc_ratio = text_similarity(target_desc, existed_desc)
        score = max(desc_ratio, title_ratio * 0.92)
        if (
            title_ratio >= SIMILARITY_TITLE_THRESHOLD
            or desc_ratio >= SIMILARITY_DESCRIPTION_THRESHOLD
        ):
            if best is None or score > best["score"]:
                best = {
                    "problem": problem,
                    "title_ratio": title_ratio,
                    "desc_ratio": desc_ratio,
                    "score": score,
                }
    return best


def build_avoid_context(
    existing_problems: list[Problem],
    rejected_candidates: list[dict],
    limit: int = 12,
) -> str:
    lines: list[str] = []

    for problem in existing_problems[:limit]:
        lines.append(
            f"- [已有] {problem.title} | {summarize_text(problem.description, 90)}"
        )

    for idx, candidate in enumerate(rejected_candidates[-4:], start=1):
        lines.append(
            f"- [已拒绝候选{idx}] {candidate['title']} | "
            f"{summarize_text(candidate['description_markdown'], 90)}"
        )

    return "\n".join(lines)


async def build_existing_problem_payload(
    db: AsyncSession,
    problem: Problem,
) -> tuple[dict, str]:
    test_case_result = await db.execute(
        select(TestCase).where(TestCase.problem_id == problem.id)
    )
    public_cases = [
        {
            "id": str(tc.id),
            "input_data": tc.input_data,
            "expected_output": tc.expected_output,
            "is_hidden": tc.is_hidden,
        }
        for tc in test_case_result.scalars().all()
        if not tc.is_hidden
    ]
    difficulty = (
        problem.difficulty.value
        if hasattr(problem.difficulty, "value")
        else str(problem.difficulty)
    )
    payload = {
        "id": str(problem.id),
        "title": problem.title,
        "difficulty": difficulty,
        "description_preview": (problem.description or "")[:220],
        "time_limit": problem.time_limit,
        "memory_limit": problem.memory_limit,
        "source_type": ProblemSourceEnum.AI_GENERATED.value,
        "is_personal": True,
        "public_test_cases": public_cases,
        "knowledge_tags": problem.knowledge_tags or [],
    }
    return payload, difficulty


def infer_knowledge_tags(title: str, description: str) -> list[str]:
    corpus = f"{title}\n{description}".lower()
    rules = {
        "数组": ["数组", "array", "双指针", "滑动窗口"],
        "字符串": ["字符串", "string", "子串", "回文"],
        "哈希": ["哈希", "hash", "字典", "map"],
        "栈": ["栈", "stack", "单调栈"],
        "队列": ["队列", "queue", "单调队列"],
        "链表": ["链表", "linked list", "listnode"],
        "二叉树": ["二叉树", "tree", "dfs", "bfs"],
        "动态规划": ["动态规划", "dp", "状态转移"],
        "贪心": ["贪心", "greedy"],
        "图论": ["图", "最短路", "并查集", "拓扑"],
        "二分": ["二分", "binary search"],
        "回溯": ["回溯", "搜索", "剪枝"],
        "数学": ["数学", "取模", "质数", "最大公约数"],
    }
    tags = [tag for tag, keywords in rules.items() if any(word in corpus for word in keywords)]
    return tags[:6]


async def estimate_user_level(
    db: AsyncSession,
    user_id,
) -> tuple[int, str]:
    official_condition = or_(
        Problem.source_type == ProblemSourceEnum.OFFICIAL,
        Problem.source_type.is_(None),
    )

    # 官方题库总数
    total_result = await db.execute(
        select(func.count(Problem.id)).where(official_condition)
    )
    total_problems = total_result.scalar() or 0

    # 用户 AC 题目数（去重，仅官方题）
    passed_result = await db.execute(
        select(func.count(distinct(Submission.problem_id)))
        .join(Problem, Problem.id == Submission.problem_id)
        .where(
            and_(
                Submission.user_id == user_id,
                Submission.status == "AC",
                Submission.run_mode == "submit",
                official_condition,
            )
        )
    )
    passed_problems = passed_result.scalar() or 0

    # 用户 AC 的难度分布（仅官方题）
    difficulty_result = await db.execute(
        select(Problem.difficulty, func.count(distinct(Submission.problem_id)))
        .join(Submission, Submission.problem_id == Problem.id)
        .where(
            and_(
                Submission.user_id == user_id,
                Submission.status == "AC",
                Submission.run_mode == "submit",
                official_condition,
            )
        )
        .group_by(Problem.difficulty)
    )

    easy_count = 0
    medium_count = 0
    hard_count = 0
    for difficulty, count in difficulty_result.all():
        difficulty_str = difficulty.value if hasattr(difficulty, "value") else str(difficulty)
        if difficulty_str == "Easy":
            easy_count = count
        elif difficulty_str == "Medium":
            medium_count = count
        elif difficulty_str == "Hard":
            hard_count = count

    completion_rate = passed_problems / total_problems if total_problems > 0 else 0.0

    base_level = 1 + int(completion_rate * 6)
    difficulty_bonus = 0
    if medium_count >= 3:
        difficulty_bonus += 1
    if hard_count >= 1:
        difficulty_bonus += 2
    elif hard_count == 0 and medium_count >= 8:
        difficulty_bonus += 1

    volume_bonus = 1 if passed_problems >= 30 else 0
    estimated_level = max(1, min(10, base_level + difficulty_bonus + volume_bonus))

    reason = (
        f"已通过 {passed_problems}/{total_problems} 题，"
        f"Easy:{easy_count} Medium:{medium_count} Hard:{hard_count}，"
        f"估计等级 L{estimated_level}"
    )
    return estimated_level, reason


@router.post("/generate-problem", response_model=dict)
async def generate_problem(
    request: GenerateProblemRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    AI 出题接口

    - progress: 根据用户刷题进度估计难度
    - custom: 使用用户指定 1-10 等级
    """
    mode = "progress" if request.mode == "estimate" else request.mode

    if mode == "custom" and request.level is None:
        return api_response(code=400, message="自定义模式需要提供 level(1-10)")

    user_id = current_user.id
    if mode == "progress":
        level, reason = await estimate_user_level(db=db, user_id=user_id)
    else:
        level = request.level or 5
        reason = f"使用自定义等级 L{level}"
    target_difficulty = level_to_difficulty(level)

    user_context = (
        f"user_id={str(user_id)}, mode={mode}, level={level}, "
        f"difficulty_hint={level_to_difficulty(level)}"
    )
    recent_ai_result = await db.execute(
        select(Problem)
        .where(
            and_(
                Problem.source_type == ProblemSourceEnum.AI_GENERATED,
                Problem.owner_id == current_user.id,
            )
        )
        .order_by(desc(Problem.created_at))
        .limit(RECENT_AI_PROBLEMS_LIMIT)
    )
    recent_ai_problems = recent_ai_result.scalars().all()

    generated: Optional[dict] = None
    similar_hit: Optional[dict] = None
    rejected_candidates: list[dict] = []
    for attempt in range(1, MAX_GENERATE_ATTEMPTS + 1):
        avoid_context = build_avoid_context(
            existing_problems=recent_ai_problems,
            rejected_candidates=rejected_candidates,
        )
        candidate = await generate_ai_problem(
            level=level,
            mode=mode,
            user_context=user_context,
            avoid_context=avoid_context,
            attempt=attempt,
        )
        similar_hit = find_similar_problem(
            title=candidate.get("title", ""),
            description=candidate.get("description_markdown", ""),
            existing_problems=recent_ai_problems,
        )
        if similar_hit is not None:
            rejected_candidates.append(
                {
                    "title": candidate.get("title", ""),
                    "description_markdown": candidate.get("description_markdown", ""),
                }
            )
            if attempt < MAX_GENERATE_ATTEMPTS:
                continue

            existing_problem = similar_hit["problem"]
            existing_payload, existing_difficulty = await build_existing_problem_payload(
                db=db,
                problem=existing_problem,
            )
            model_difficulty = (
                candidate.get("difficulty_label")
                or level_to_difficulty(level)
            )
            similarity_note = (
                f"候选题与历史题相似度过高（标题 {similar_hit['title_ratio']:.2f} / "
                f"题干 {similar_hit['desc_ratio']:.2f}），已返回你已有题目。"
            )
            return api_response(
                code=0,
                message="检测到高相似题目，已返回你已生成的题",
                data={
                    "mode": mode,
                    "generated_level": level,
                    "level_reason": reason,
                    "generation_source": "deduplicated_similarity",
                    "generation_note": similarity_note,
                    "deduplicated": True,
                    "difficulty_calibration": {
                        "target": target_difficulty,
                        "model_output": model_difficulty,
                        "final": existing_difficulty,
                        "adjusted": existing_difficulty != model_difficulty,
                    },
                    "problem": existing_payload,
                },
            )

        generated = candidate
        break

    if generated is None:
        generated = await generate_ai_problem(
            level=level,
            mode=mode,
            user_context=user_context,
            avoid_context=build_avoid_context(recent_ai_problems, rejected_candidates),
            attempt=MAX_GENERATE_ATTEMPTS,
        )

    generation_source = generated.get("generation_source", "llm")
    generation_note = generated.get("generation_note", "")

    model_difficulty = generated.get("difficulty_label") or target_difficulty
    calibrated_difficulty = (
        model_difficulty if model_difficulty == target_difficulty else target_difficulty
    )
    difficulty_adjusted = model_difficulty != calibrated_difficulty

    title = generated["title"]
    description_markdown = generated["description_markdown"]
    title_hash = content_hash(title)
    description_hash = content_hash(description_markdown)

    existed_result = await db.execute(
        select(Problem).where(
            and_(
                Problem.source_type == ProblemSourceEnum.AI_GENERATED,
                Problem.owner_id == current_user.id,
                or_(
                    Problem.title_hash == title_hash,
                    Problem.description_hash == description_hash,
                ),
            )
        )
    )
    existed_problem = existed_result.scalar_one_or_none()
    if existed_problem:
        existing_payload, existed_difficulty = await build_existing_problem_payload(
            db=db,
            problem=existed_problem,
        )
        return api_response(
            code=0,
            message="检测到相似题目，已返回你已生成的题",
            data={
                "mode": mode,
                "generated_level": level,
                "level_reason": reason,
                "generation_source": "deduplicated",
                "generation_note": "命中题干/标题哈希去重，避免重复生成",
                "deduplicated": True,
                "difficulty_calibration": {
                    "target": target_difficulty,
                    "model_output": model_difficulty,
                    "final": existed_difficulty,
                    "adjusted": existed_difficulty != model_difficulty,
                },
                "problem": existing_payload,
            },
        )

    # 写入题库
    try:
        difficulty_enum = DifficultyEnum(calibrated_difficulty)
    except Exception:
        difficulty_enum = DifficultyEnum(target_difficulty)

    new_problem = Problem(
        title=title,
        description=description_markdown,
        difficulty=difficulty_enum,
        time_limit=generated["time_limit"],
        memory_limit=generated["memory_limit"],
        source_type=ProblemSourceEnum.AI_GENERATED,
        owner_id=current_user.id,
        knowledge_tags=infer_knowledge_tags(title, description_markdown),
        title_hash=title_hash,
        description_hash=description_hash,
    )
    db.add(new_problem)
    await db.flush()

    created_cases = []
    for case in generated["test_cases"]:
        test_case = TestCase(
            problem_id=str(new_problem.id),
            input_data=case["input_data"],
            expected_output=case["expected_output"],
            is_hidden=case.get("is_hidden", False),
        )
        db.add(test_case)
        created_cases.append(test_case)

    await db.commit()
    await db.refresh(new_problem)

    public_cases = [
        {
            "id": str(tc.id),
            "input_data": tc.input_data,
            "expected_output": tc.expected_output,
            "is_hidden": tc.is_hidden,
        }
        for tc in created_cases
        if not tc.is_hidden
    ]

    return api_response(
        code=0,
        message="AI 出题成功",
        data={
            "mode": mode,
            "generated_level": level,
            "level_reason": reason,
            "generation_source": generation_source,
            "generation_note": generation_note,
            "deduplicated": False,
            "difficulty_calibration": {
                "target": target_difficulty,
                "model_output": model_difficulty,
                "final": calibrated_difficulty,
                "adjusted": difficulty_adjusted,
            },
            "problem": {
                "id": str(new_problem.id),
                "title": new_problem.title,
                "difficulty": calibrated_difficulty,
                "description_preview": new_problem.description[:220],
                "time_limit": new_problem.time_limit,
                "memory_limit": new_problem.memory_limit,
                "source_type": ProblemSourceEnum.AI_GENERATED.value,
                "is_personal": True,
                "public_test_cases": public_cases,
                "knowledge_tags": new_problem.knowledge_tags or [],
            },
        },
    )


@router.post("/problems/{problem_id}/feedback", response_model=dict)
async def feedback_ai_problem(
    problem_id: str,
    request: ProblemFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    problem_result = await db.execute(
        select(Problem).where(
            and_(
                Problem.id == problem_id,
                Problem.source_type == ProblemSourceEnum.AI_GENERATED,
                visible_problem_condition(current_user.id),
            )
        )
    )
    problem = problem_result.scalar_one_or_none()
    if not problem:
        return api_response(code=404, message="AI 题目不存在或无权限访问")

    vote_value = 1 if request.vote == "up" else -1
    feedback_result = await db.execute(
        select(AiProblemFeedback).where(
            and_(
                AiProblemFeedback.problem_id == problem.id,
                AiProblemFeedback.user_id == current_user.id,
            )
        )
    )
    feedback = feedback_result.scalar_one_or_none()

    delta = vote_value
    if feedback is None:
        feedback = AiProblemFeedback(
            problem_id=problem.id,
            user_id=current_user.id,
            vote=vote_value,
            reason=request.reason,
        )
        db.add(feedback)
    else:
        delta = vote_value - (feedback.vote or 0)
        feedback.vote = vote_value
        feedback.reason = request.reason

    problem.ai_feedback_score = int(problem.ai_feedback_score or 0) + delta
    await db.commit()

    return api_response(
        code=0,
        message="反馈已记录",
        data={
            "problem_id": str(problem.id),
            "your_vote": vote_value,
            "feedback_score": int(problem.ai_feedback_score or 0),
            "updated": delta != 0,
        },
    )
