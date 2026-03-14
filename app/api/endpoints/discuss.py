"""
讨论区 API 接口
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.problem import Comment, Post, Problem, ProblemSourceEnum, SharedProblem
from app.schemas.response import api_response
from app.api.endpoints.auth import get_current_user


router = APIRouter(prefix="/api/discuss", tags=["讨论区"])


class PostCreateRequest(BaseModel):
    problem_id: str
    content: str


class CommentCreateRequest(BaseModel):
    post_id: str
    content: str


class PostOut(BaseModel):
    id: str
    user_id: str
    problem_id: str
    content: str
    created_at: str
    user: dict = None
    comments: List[dict] = []


async def ensure_problem_access(
    problem_id: str,
    current_user: User,
    db: AsyncSession,
):
    """
    讨论区可见性规则:
    - 官方题: 全员可讨论
    - AI 私有题: 题主本人可讨论
    - 已分享到广场的 AI 题: 登录用户可讨论
    """
    shared_problem_ids = select(SharedProblem.problem_id)
    result = await db.execute(
        select(Problem).where(
            and_(
                Problem.id == problem_id,
                or_(
                    Problem.source_type == ProblemSourceEnum.OFFICIAL,
                    Problem.source_type.is_(None),
                    and_(
                        Problem.source_type == ProblemSourceEnum.AI_GENERATED,
                        Problem.owner_id == current_user.id,
                    ),
                    and_(
                        Problem.source_type == ProblemSourceEnum.AI_GENERATED,
                        Problem.id.in_(shared_problem_ids),
                    ),
                ),
            )
        )
    )
    return result.scalar_one_or_none()


@router.get("/{problem_id}", response_model=dict)
async def get_posts(
    problem_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取题目的讨论帖子"""
    problem = await ensure_problem_access(
        problem_id=problem_id,
        current_user=current_user,
        db=db,
    )
    if not problem:
        return api_response(code=404, message="题目不存在或无权限访问")

    offset = (page - 1) * page_size

    result = await db.execute(
        select(Post)
        .where(Post.problem_id == problem_id)
        .options(selectinload(Post.user))
        .order_by(desc(Post.created_at))
        .offset(offset)
        .limit(page_size)
    )
    posts = result.scalars().all()

    # 获取每个帖子的评论
    posts_with_comments = []
    for post in posts:
        # 获取评论
        comment_result = await db.execute(
            select(Comment)
            .where(Comment.post_id == post.id)
            .options(selectinload(Comment.user))
            .order_by(desc(Comment.created_at))
        )
        comments = comment_result.scalars().all()

        post_dict = {
            "id": str(post.id),
            "user_id": str(post.user_id),
            "problem_id": str(post.problem_id),
            "content": post.content,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "user": {"id": str(post.user.id), "username": post.user.username}
            if post.user
            else None,
            "comments": [
                {
                    "id": str(c.id),
                    "user_id": str(c.user_id),
                    "content": c.content,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "user": {"id": str(c.user.id), "username": c.user.username}
                    if c.user
                    else None,
                }
                for c in comments
            ],
        }
        posts_with_comments.append(post_dict)

    return api_response(
        data={
            "items": posts_with_comments,
            "total": len(posts_with_comments),
            "page": page,
            "page_size": page_size,
        },
        code=0,
    )


@router.post("", response_model=dict)
async def create_post(
    post_data: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """创建讨论帖子"""
    problem = await ensure_problem_access(
        problem_id=post_data.problem_id,
        current_user=current_user,
        db=db,
    )
    if not problem:
        return api_response(code=404, message="题目不存在或无权限访问")

    post = Post(
        user_id=str(current_user.id),
        problem_id=post_data.problem_id,
        content=post_data.content,
    )
    db.add(post)
    await db.commit()

    return api_response(
        data={
            "id": str(post.id),
            "user_id": str(post.user_id),
            "problem_id": str(post.problem_id),
            "content": post.content,
            "created_at": post.created_at.isoformat() if post.created_at else None,
        },
        message="发布成功",
        code=0,
    )


@router.delete("/{post_id}", response_model=dict)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """删除帖子"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        return api_response(code=404, message="帖子不存在")

    problem = await ensure_problem_access(
        problem_id=str(post.problem_id),
        current_user=current_user,
        db=db,
    )
    if not problem:
        return api_response(code=404, message="帖子不存在或无权限访问")

    # 检查是否是帖子作者
    if str(post.user_id) != str(current_user.id):
        return api_response(code=403, message="只能删除自己的帖子")

    await db.delete(post)
    await db.commit()

    return api_response(message="删除成功", code=0)


@router.post("/comment", response_model=dict)
async def create_comment(
    comment_data: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """添加评论"""
    post_result = await db.execute(select(Post).where(Post.id == comment_data.post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        return api_response(code=404, message="帖子不存在")

    problem = await ensure_problem_access(
        problem_id=str(post.problem_id),
        current_user=current_user,
        db=db,
    )
    if not problem:
        return api_response(code=404, message="帖子不存在或无权限访问")

    comment = Comment(
        user_id=str(current_user.id),
        post_id=comment_data.post_id,
        content=comment_data.content,
    )
    db.add(comment)
    await db.commit()

    return api_response(
        data={
            "id": str(comment.id),
            "user_id": str(comment.user_id),
            "post_id": str(comment.post_id),
            "content": comment.content,
            "created_at": comment.created_at.isoformat()
            if comment.created_at
            else None,
        },
        message="评论成功",
        code=0,
    )


@router.delete("/comment/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """删除评论（楼主或评论作者）"""
    # 1) 查询评论
    comment_result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = comment_result.scalar_one_or_none()
    if not comment:
        return api_response(code=404, message="评论不存在")

    # 2) 查询评论所属帖子（用于楼主权限校验）
    post_result = await db.execute(select(Post).where(Post.id == comment.post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        return api_response(code=404, message="帖子不存在")

    problem = await ensure_problem_access(
        problem_id=str(post.problem_id),
        current_user=current_user,
        db=db,
    )
    if not problem:
        return api_response(code=404, message="评论不存在或无权限访问")

    current_user_id = str(current_user.id)
    is_post_owner = str(post.user_id) == current_user_id
    is_comment_owner = str(comment.user_id) == current_user_id

    if not (is_post_owner or is_comment_owner):
        return api_response(code=403, message="仅楼主或评论作者可删除评论")

    await db.delete(comment)
    await db.commit()

    return api_response(message="评论删除成功", code=0)
