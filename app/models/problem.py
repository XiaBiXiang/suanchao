"""
题目数据模型
使用 SQLAlchemy 2.0 异步 ORM
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.user import User


class DifficultyEnum(str, Enum):
    """
    题目难度枚举
    """

    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class ProblemSourceEnum(str, Enum):
    """
    题目来源枚举
    """

    OFFICIAL = "official"
    AI_GENERATED = "ai_generated"


class Problem(Base):
    """
    题目表模型

    字段说明:
        id: 主键 UUID
        title: 题目标题
        description: 题目描述 (支持 Markdown)
        difficulty: 难度等级 (Easy/Medium/Hard)
        time_limit: 时间限制 (毫秒)
        memory_limit: 内存限制 (MB)
        created_at: 创建时间
    """

    __tablename__ = "problems"

    # 主键 UUID
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
        comment="题目唯一标识",
    )

    # 标题
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="题目标题")

    # 描述 (支持 Markdown)
    description: Mapped[str] = mapped_column(
        Text, nullable=False, default="", comment="题目描述"
    )

    # 难度等级
    difficulty: Mapped[str] = mapped_column(
        SQLEnum(DifficultyEnum),
        nullable=False,
        default=DifficultyEnum.EASY,
        comment="难度等级",
    )

    # 时间限制 (毫秒)
    time_limit: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1000, comment="时间限制 (毫秒)"
    )

    # 内存限制 (MB)
    memory_limit: Mapped[int] = mapped_column(
        Integer, nullable=False, default=128, comment="内存限制 (MB)"
    )

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, comment="创建时间"
    )

    # 题目来源
    source_type: Mapped[str] = mapped_column(
        SQLEnum(ProblemSourceEnum),
        nullable=False,
        default=ProblemSourceEnum.OFFICIAL,
        comment="题目来源（官方/AI）",
    )

    # 归属用户（AI 私有题）
    owner_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="归属用户ID（仅 AI 私有题）",
    )

    # 是否由广场导入
    is_square_imported: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否由广场导入",
    )

    # 知识点标签（用于错题本按知识点复习）
    knowledge_tags: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="知识点标签",
    )

    # AI 出题去重哈希
    title_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="题目标题哈希",
    )
    description_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="题目描述哈希",
    )

    # AI 题目反馈累计分
    ai_feedback_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="AI 题目反馈分（up/down）",
    )

    # 关联测试用例 (一对多)
    test_cases: Mapped[List["TestCase"]] = relationship(
        "TestCase",
        back_populates="problem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Problem(id={self.id}, title={self.title}, difficulty={self.difficulty}, source={self.source_type})>"
        )


class TestCase(Base):
    """
    测试用例表模型

    字段说明:
        id: 主键 UUID
        problem_id: 关联的题目 ID
        input_data: 输入数据
        expected_output: 期望输出
        is_hidden: 是否隐藏 (隐藏用例不显示给用户)
    """

    __tablename__ = "test_cases"

    # 主键 UUID
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
        comment="测试用例唯一标识",
    )

    # 关联题目 ID
    problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联题目ID",
    )

    # 输入数据
    input_data: Mapped[str] = mapped_column(Text, nullable=False, comment="输入数据")

    # 期望输出
    expected_output: Mapped[str] = mapped_column(
        Text, nullable=False, comment="期望输出"
    )

    # 是否隐藏
    is_hidden: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否隐藏 (隐藏用例)"
    )

    # 关联题目 (多对一)
    problem: Mapped["Problem"] = relationship("Problem", back_populates="test_cases")

    def __repr__(self) -> str:
        return f"<TestCase(id={self.id}, problem_id={self.problem_id}, is_hidden={self.is_hidden})>"


class Submission(Base):
    """
    用户提交记录表

    字段说明:
        id: 主键 UUID
        user_id: 用户 ID
        problem_id: 题目 ID
        code: 提交的代码
        language: 编程语言
        status: 提交状态 (AC/WA/TLE/MLE/RE/CE)
        passed_cases: 通过的用例数
        total_cases: 总用例数
        created_at: 提交时间
    """

    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(Text, nullable=False)

    language: Mapped[str] = mapped_column(String(50), nullable=False, default="python")

    status: Mapped[str] = mapped_column(String(20), nullable=False)

    passed_cases: Mapped[int] = mapped_column(Integer, default=0)

    total_cases: Mapped[int] = mapped_column(Integer, default=0)

    run_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="submit",
        comment="执行模式：run/submit",
    )

    custom_input: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="自定义输入（run 模式）",
    )

    total_time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="总耗时（毫秒）",
    )

    max_memory_mb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="峰值内存（MB）",
    )

    result_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="判题详细结果（JSON）",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Submission(id={self.id}, user_id={self.user_id}, problem_id={self.problem_id}, status={self.status})>"


class Post(Base):
    """
    讨论帖子表
    """

    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    user: Mapped["User"] = relationship("User")


class Comment(Base):
    """
    评论表
    """

    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    post_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    user: Mapped["User"] = relationship("User")


class SharedProblem(Base):
    """
    广场分享题目
    """

    __tablename__ = "shared_problems"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    owner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    import_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    star_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class SharedProblemStar(Base):
    """
    广场题目 Star 记录（同一用户对同一分享仅可 Star 一次）
    """

    __tablename__ = "shared_problem_stars"
    __table_args__ = (
        UniqueConstraint(
            "shared_problem_id",
            "user_id",
            name="uq_shared_problem_stars_share_user",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    shared_problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class SharedProblemImport(Base):
    """
    广场题目导入记录
    """

    __tablename__ = "shared_problem_imports"
    __table_args__ = (
        UniqueConstraint(
            "shared_problem_id",
            "user_id",
            name="uq_shared_problem_imports_share_user",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    shared_problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shared_problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    imported_problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class JudgeJob(Base):
    """
    异步判题任务队列项
    """

    __tablename__ = "judge_jobs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="python")
    run_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="submit",
        comment="执行模式：run/submit",
    )
    custom_input: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="queued",
        index=True,
        comment="queued/running/completed/failed",
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="任务进度 0-100",
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class WrongProblemNote(Base):
    """
    错题本条目（支持知识点复习与二刷提醒）
    """

    __tablename__ = "wrong_problem_notes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "problem_id",
            name="uq_wrong_problem_notes_user_problem",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    knowledge_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    last_wrong_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_review_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class AiProblemFeedback(Base):
    """
    AI 题目反馈（用户有用/无用）
    """

    __tablename__ = "ai_problem_feedbacks"
    __table_args__ = (
        UniqueConstraint(
            "problem_id",
            "user_id",
            name="uq_ai_problem_feedbacks_problem_user",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__("uuid").uuid4()),
    )

    problem_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vote: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="1=有用, -1=无用",
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
