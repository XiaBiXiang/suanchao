"""add problem source and owner

Revision ID: 20260309_0002
Revises: 20260309_0001
Create Date: 2026-03-09 16:18:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260309_0002"
down_revision: Union[str, Sequence[str], None] = "20260309_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    problem_columns = {column["name"] for column in inspector.get_columns("problems")}

    problem_source_enum = sa.Enum(
        "OFFICIAL", "AI_GENERATED", name="problemsourceenum"
    )
    problem_source_enum.create(bind, checkfirst=True)

    if "source_type" not in problem_columns:
        op.add_column(
            "problems",
            sa.Column(
                "source_type",
                problem_source_enum,
                nullable=True,
            ),
        )

    if "owner_id" not in problem_columns:
        op.add_column(
            "problems",
            sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        )

    index_names = {index["name"] for index in inspector.get_indexes("problems")}
    if op.f("ix_problems_owner_id") not in index_names:
        op.create_index(
            op.f("ix_problems_owner_id"), "problems", ["owner_id"], unique=False
        )

    fk_names = {fk["name"] for fk in inspector.get_foreign_keys("problems")}
    if "fk_problems_owner_id_users" not in fk_names:
        op.create_foreign_key(
            "fk_problems_owner_id_users",
            source_table="problems",
            referent_table="users",
            local_cols=["owner_id"],
            remote_cols=["id"],
            ondelete="SET NULL",
        )

    # 为历史数据补默认来源，并收紧为非空
    op.execute("UPDATE problems SET source_type = 'OFFICIAL' WHERE source_type IS NULL")
    op.alter_column("problems", "source_type", nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    problem_columns = {column["name"] for column in inspector.get_columns("problems")}
    index_names = {index["name"] for index in inspector.get_indexes("problems")}
    fk_names = {fk["name"] for fk in inspector.get_foreign_keys("problems")}

    problem_source_enum = sa.Enum(
        "OFFICIAL", "AI_GENERATED", name="problemsourceenum"
    )

    if "fk_problems_owner_id_users" in fk_names:
        op.drop_constraint("fk_problems_owner_id_users", "problems", type_="foreignkey")
    if op.f("ix_problems_owner_id") in index_names:
        op.drop_index(op.f("ix_problems_owner_id"), table_name="problems")
    if "owner_id" in problem_columns:
        op.drop_column("problems", "owner_id")
    if "source_type" in problem_columns:
        op.drop_column("problems", "source_type")
    problem_source_enum.drop(bind, checkfirst=True)
