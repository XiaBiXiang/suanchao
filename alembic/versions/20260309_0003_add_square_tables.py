"""add square share/import tables

Revision ID: 20260309_0003
Revises: 20260309_0002
Create Date: 2026-03-09 22:40:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260309_0003"
down_revision: Union[str, Sequence[str], None] = "20260309_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "shared_problems" not in tables:
        op.create_table(
            "shared_problems",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("problem_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column(
                "import_count",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(
                ["problem_id"], ["problems.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("problem_id"),
        )
        op.create_index(
            op.f("ix_shared_problems_problem_id"),
            "shared_problems",
            ["problem_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_shared_problems_owner_id"),
            "shared_problems",
            ["owner_id"],
            unique=False,
        )

    tables = set(sa.inspect(bind).get_table_names())
    if "shared_problem_imports" not in tables:
        op.create_table(
            "shared_problem_imports",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column(
                "shared_problem_id", postgresql.UUID(as_uuid=True), nullable=False
            ),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("imported_problem_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(
                ["shared_problem_id"], ["shared_problems.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["imported_problem_id"], ["problems.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "shared_problem_id",
                "user_id",
                name="uq_shared_problem_imports_share_user",
            ),
        )
        op.create_index(
            op.f("ix_shared_problem_imports_shared_problem_id"),
            "shared_problem_imports",
            ["shared_problem_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_shared_problem_imports_user_id"),
            "shared_problem_imports",
            ["user_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_shared_problem_imports_imported_problem_id"),
            "shared_problem_imports",
            ["imported_problem_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "shared_problem_imports" in tables:
        index_names = {
            index["name"] for index in inspector.get_indexes("shared_problem_imports")
        }
        if op.f("ix_shared_problem_imports_imported_problem_id") in index_names:
            op.drop_index(
                op.f("ix_shared_problem_imports_imported_problem_id"),
                table_name="shared_problem_imports",
            )
        if op.f("ix_shared_problem_imports_user_id") in index_names:
            op.drop_index(
                op.f("ix_shared_problem_imports_user_id"),
                table_name="shared_problem_imports",
            )
        if op.f("ix_shared_problem_imports_shared_problem_id") in index_names:
            op.drop_index(
                op.f("ix_shared_problem_imports_shared_problem_id"),
                table_name="shared_problem_imports",
            )
        op.drop_table("shared_problem_imports")

    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "shared_problems" in tables:
        index_names = {index["name"] for index in inspector.get_indexes("shared_problems")}
        if op.f("ix_shared_problems_owner_id") in index_names:
            op.drop_index(op.f("ix_shared_problems_owner_id"), table_name="shared_problems")
        if op.f("ix_shared_problems_problem_id") in index_names:
            op.drop_index(op.f("ix_shared_problems_problem_id"), table_name="shared_problems")
        op.drop_table("shared_problems")
