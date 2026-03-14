"""add problem is_square_imported flag

Revision ID: 20260310_0004
Revises: 20260309_0003
Create Date: 2026-03-10 10:15:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260310_0004"
down_revision: Union[str, Sequence[str], None] = "20260309_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("problems")}

    if "is_square_imported" not in columns:
        op.add_column(
            "problems",
            sa.Column(
                "is_square_imported",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )

    op.execute(
        "UPDATE problems SET is_square_imported = false WHERE is_square_imported IS NULL"
    )
    op.alter_column(
        "problems",
        "is_square_imported",
        server_default=None,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("problems")}

    if "is_square_imported" in columns:
        op.drop_column("problems", "is_square_imported")
