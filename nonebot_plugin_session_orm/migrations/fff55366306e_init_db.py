"""init_db

修订 ID: fff55366306e
父修订:
创建时间: 2023-10-07 16:34:54.127642

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "fff55366306e"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = ("nonebot_plugin_session_orm",)
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "nonebot_plugin_session_orm_sessionmodel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bot_id", sa.String(length=64), nullable=False),
        sa.Column("bot_type", sa.String(length=32), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("id1", sa.String(length=64), nullable=False),
        sa.Column("id2", sa.String(length=64), nullable=False),
        sa.Column("id3", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_nonebot_plugin_session_orm_sessionmodel")
        ),
        sa.UniqueConstraint(
            "bot_id",
            "bot_type",
            "platform",
            "level",
            "id1",
            "id2",
            "id3",
            name="unique_session",
        ),
    )
    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("nonebot_plugin_session_orm_sessionmodel")
    # ### end Alembic commands ###
