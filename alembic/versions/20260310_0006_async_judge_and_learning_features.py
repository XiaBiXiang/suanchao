"""add async judge queue and learning feature schema

Revision ID: 20260310_0006
Revises: 20260310_0005
Create Date: 2026-03-10 13:45:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260310_0006"
down_revision: Union[str, Sequence[str], None] = "20260310_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_columns(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _table_indexes(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # problems 新增字段
    problem_columns = _table_columns(inspector, "problems")
    if "knowledge_tags" not in problem_columns:
        op.add_column(
            "problems",
            sa.Column(
                "knowledge_tags",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::json"),
            ),
        )
    if "title_hash" not in problem_columns:
        op.add_column("problems", sa.Column("title_hash", sa.String(length=64), nullable=True))
    if "description_hash" not in problem_columns:
        op.add_column(
            "problems",
            sa.Column("description_hash", sa.String(length=64), nullable=True),
        )
    if "ai_feedback_score" not in problem_columns:
        op.add_column(
            "problems",
            sa.Column(
                "ai_feedback_score",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )

    op.execute("UPDATE problems SET knowledge_tags = '[]'::json WHERE knowledge_tags IS NULL")
    op.execute("UPDATE problems SET ai_feedback_score = 0 WHERE ai_feedback_score IS NULL")
    op.alter_column("problems", "knowledge_tags", server_default=None)
    op.alter_column("problems", "ai_feedback_score", server_default=None)

    problem_indexes = _table_indexes(sa.inspect(bind), "problems")
    if op.f("ix_problems_title_hash") not in problem_indexes:
        op.create_index(op.f("ix_problems_title_hash"), "problems", ["title_hash"], unique=False)
    if op.f("ix_problems_description_hash") not in problem_indexes:
        op.create_index(
            op.f("ix_problems_description_hash"),
            "problems",
            ["description_hash"],
            unique=False,
        )

    # submissions 新增字段
    submission_columns = _table_columns(sa.inspect(bind), "submissions")
    if "run_mode" not in submission_columns:
        op.add_column(
            "submissions",
            sa.Column(
                "run_mode",
                sa.String(length=20),
                nullable=False,
                server_default="submit",
            ),
        )
    if "custom_input" not in submission_columns:
        op.add_column("submissions", sa.Column("custom_input", sa.Text(), nullable=True))
    if "total_time_ms" not in submission_columns:
        op.add_column(
            "submissions",
            sa.Column(
                "total_time_ms",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )
    if "max_memory_mb" not in submission_columns:
        op.add_column(
            "submissions",
            sa.Column(
                "max_memory_mb",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )
    if "result_data" not in submission_columns:
        op.add_column("submissions", sa.Column("result_data", sa.JSON(), nullable=True))

    op.execute("UPDATE submissions SET run_mode = 'submit' WHERE run_mode IS NULL")
    op.execute("UPDATE submissions SET total_time_ms = 0 WHERE total_time_ms IS NULL")
    op.execute("UPDATE submissions SET max_memory_mb = 0 WHERE max_memory_mb IS NULL")
    op.alter_column("submissions", "run_mode", server_default=None)
    op.alter_column("submissions", "total_time_ms", server_default=None)
    op.alter_column("submissions", "max_memory_mb", server_default=None)

    tables = set(sa.inspect(bind).get_table_names())

    # 异步判题任务表
    if "judge_jobs" not in tables:
        op.create_table(
            "judge_jobs",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("problem_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("code", sa.Text(), nullable=False),
            sa.Column("language", sa.String(length=50), nullable=False, server_default="python"),
            sa.Column("run_mode", sa.String(length=20), nullable=False, server_default="submit"),
            sa.Column("custom_input", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
            sa.Column("progress", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("result_data", sa.JSON(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_judge_jobs_user_id"), "judge_jobs", ["user_id"], unique=False)
        op.create_index(
            op.f("ix_judge_jobs_problem_id"),
            "judge_jobs",
            ["problem_id"],
            unique=False,
        )
        op.create_index(op.f("ix_judge_jobs_status"), "judge_jobs", ["status"], unique=False)
        op.create_index(
            op.f("ix_judge_jobs_created_at"),
            "judge_jobs",
            ["created_at"],
            unique=False,
        )

    # 错题本表
    tables = set(sa.inspect(bind).get_table_names())
    if "wrong_problem_notes" not in tables:
        op.create_table(
            "wrong_problem_notes",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("problem_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("wrong_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("review_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column(
                "knowledge_tags",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::json"),
            ),
            sa.Column("last_wrong_at", sa.DateTime(), nullable=True),
            sa.Column("last_review_at", sa.DateTime(), nullable=True),
            sa.Column("next_review_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "user_id",
                "problem_id",
                name="uq_wrong_problem_notes_user_problem",
            ),
        )
        op.create_index(
            op.f("ix_wrong_problem_notes_user_id"),
            "wrong_problem_notes",
            ["user_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_wrong_problem_notes_problem_id"),
            "wrong_problem_notes",
            ["problem_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_wrong_problem_notes_next_review_at"),
            "wrong_problem_notes",
            ["next_review_at"],
            unique=False,
        )
        op.execute(
            "UPDATE wrong_problem_notes SET knowledge_tags = '[]'::json WHERE knowledge_tags IS NULL"
        )
        op.alter_column("wrong_problem_notes", "knowledge_tags", server_default=None)
        op.alter_column("wrong_problem_notes", "wrong_count", server_default=None)
        op.alter_column("wrong_problem_notes", "review_count", server_default=None)
        op.alter_column("wrong_problem_notes", "is_resolved", server_default=None)

    # AI 题目反馈表
    tables = set(sa.inspect(bind).get_table_names())
    if "ai_problem_feedbacks" not in tables:
        op.create_table(
            "ai_problem_feedbacks",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("problem_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("vote", sa.Integer(), nullable=False),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "problem_id",
                "user_id",
                name="uq_ai_problem_feedbacks_problem_user",
            ),
        )
        op.create_index(
            op.f("ix_ai_problem_feedbacks_problem_id"),
            "ai_problem_feedbacks",
            ["problem_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_ai_problem_feedbacks_user_id"),
            "ai_problem_feedbacks",
            ["user_id"],
            unique=False,
        )

    tables = set(sa.inspect(bind).get_table_names())
    if "judge_jobs" in tables:
        judge_columns = _table_columns(sa.inspect(bind), "judge_jobs")
        if "language" in judge_columns:
            op.alter_column("judge_jobs", "language", server_default=None)
        if "run_mode" in judge_columns:
            op.alter_column("judge_jobs", "run_mode", server_default=None)
        if "status" in judge_columns:
            op.alter_column("judge_jobs", "status", server_default=None)
        if "progress" in judge_columns:
            op.alter_column("judge_jobs", "progress", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "ai_problem_feedbacks" in tables:
        index_names = _table_indexes(inspector, "ai_problem_feedbacks")
        if op.f("ix_ai_problem_feedbacks_user_id") in index_names:
            op.drop_index(
                op.f("ix_ai_problem_feedbacks_user_id"),
                table_name="ai_problem_feedbacks",
            )
        if op.f("ix_ai_problem_feedbacks_problem_id") in index_names:
            op.drop_index(
                op.f("ix_ai_problem_feedbacks_problem_id"),
                table_name="ai_problem_feedbacks",
            )
        op.drop_table("ai_problem_feedbacks")

    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "wrong_problem_notes" in tables:
        index_names = _table_indexes(inspector, "wrong_problem_notes")
        if op.f("ix_wrong_problem_notes_next_review_at") in index_names:
            op.drop_index(
                op.f("ix_wrong_problem_notes_next_review_at"),
                table_name="wrong_problem_notes",
            )
        if op.f("ix_wrong_problem_notes_problem_id") in index_names:
            op.drop_index(
                op.f("ix_wrong_problem_notes_problem_id"),
                table_name="wrong_problem_notes",
            )
        if op.f("ix_wrong_problem_notes_user_id") in index_names:
            op.drop_index(
                op.f("ix_wrong_problem_notes_user_id"),
                table_name="wrong_problem_notes",
            )
        op.drop_table("wrong_problem_notes")

    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "judge_jobs" in tables:
        index_names = _table_indexes(inspector, "judge_jobs")
        if op.f("ix_judge_jobs_created_at") in index_names:
            op.drop_index(op.f("ix_judge_jobs_created_at"), table_name="judge_jobs")
        if op.f("ix_judge_jobs_status") in index_names:
            op.drop_index(op.f("ix_judge_jobs_status"), table_name="judge_jobs")
        if op.f("ix_judge_jobs_problem_id") in index_names:
            op.drop_index(op.f("ix_judge_jobs_problem_id"), table_name="judge_jobs")
        if op.f("ix_judge_jobs_user_id") in index_names:
            op.drop_index(op.f("ix_judge_jobs_user_id"), table_name="judge_jobs")
        op.drop_table("judge_jobs")

    submission_columns = _table_columns(sa.inspect(bind), "submissions")
    if "result_data" in submission_columns:
        op.drop_column("submissions", "result_data")
    if "max_memory_mb" in submission_columns:
        op.drop_column("submissions", "max_memory_mb")
    if "total_time_ms" in submission_columns:
        op.drop_column("submissions", "total_time_ms")
    if "custom_input" in submission_columns:
        op.drop_column("submissions", "custom_input")
    if "run_mode" in submission_columns:
        op.drop_column("submissions", "run_mode")

    inspector = sa.inspect(bind)
    problem_columns = _table_columns(inspector, "problems")
    problem_indexes = _table_indexes(inspector, "problems")
    if op.f("ix_problems_description_hash") in problem_indexes:
        op.drop_index(op.f("ix_problems_description_hash"), table_name="problems")
    if op.f("ix_problems_title_hash") in problem_indexes:
        op.drop_index(op.f("ix_problems_title_hash"), table_name="problems")
    if "ai_feedback_score" in problem_columns:
        op.drop_column("problems", "ai_feedback_score")
    if "description_hash" in problem_columns:
        op.drop_column("problems", "description_hash")
    if "title_hash" in problem_columns:
        op.drop_column("problems", "title_hash")
    if "knowledge_tags" in problem_columns:
        op.drop_column("problems", "knowledge_tags")
