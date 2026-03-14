"""add square stars table and star_count

Revision ID: 20260310_0005
Revises: 20260310_0004
Create Date: 2026-03-10 11:35:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260310_0005"
down_revision: Union[str, Sequence[str], None] = "20260310_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    shared_columns = {
        column["name"] for column in inspector.get_columns("shared_problems")
    }
    if "star_count" not in shared_columns:
        op.add_column(
            "shared_problems",
            sa.Column(
                "star_count",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )
    op.execute("UPDATE shared_problems SET star_count = 0 WHERE star_count IS NULL")
    op.alter_column(
        "shared_problems",
        "star_count",
        nullable=False,
        server_default=None,
    )

    tables = set(sa.inspect(bind).get_table_names())
    if "shared_problem_stars" not in tables:
        op.create_table(
            "shared_problem_stars",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column(
                "shared_problem_id", postgresql.UUID(as_uuid=True), nullable=False
            ),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
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
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "shared_problem_id",
                "user_id",
                name="uq_shared_problem_stars_share_user",
            ),
        )
        op.create_index(
            op.f("ix_shared_problem_stars_shared_problem_id"),
            "shared_problem_stars",
            ["shared_problem_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_shared_problem_stars_user_id"),
            "shared_problem_stars",
            ["user_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "shared_problem_stars" in tables:
        index_names = {
            index["name"] for index in inspector.get_indexes("shared_problem_stars")
        }
        if op.f("ix_shared_problem_stars_user_id") in index_names:
            op.drop_index(
                op.f("ix_shared_problem_stars_user_id"),
                table_name="shared_problem_stars",
            )
        if op.f("ix_shared_problem_stars_shared_problem_id") in index_names:
            op.drop_index(
                op.f("ix_shared_problem_stars_shared_problem_id"),
                table_name="shared_problem_stars",
            )
        op.drop_table("shared_problem_stars")

    shared_columns = {
        column["name"] for column in sa.inspect(bind).get_columns("shared_problems")
    }
    if "star_count" in shared_columns:
        op.drop_column("shared_problems", "star_count")
