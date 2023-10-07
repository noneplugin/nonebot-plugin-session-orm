from typing import List, Union

from nonebot_plugin_orm import Model, get_session
from nonebot_plugin_session import Session, SessionIdType, SessionLevel
from sqlalchemy import Integer, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import ColumnElement


class SessionModel(Model):
    __table_args__ = (
        UniqueConstraint(
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

    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[str] = mapped_column(String(64))
    bot_type: Mapped[str] = mapped_column(String(32))
    platform: Mapped[str] = mapped_column(String(32))
    level: Mapped[int] = mapped_column(Integer)
    id1: Mapped[str] = mapped_column(String(64))
    id2: Mapped[str] = mapped_column(String(64))
    id3: Mapped[str] = mapped_column(String(64))

    @property
    def session(self) -> Session:
        return Session(
            bot_id=self.bot_id,
            bot_type=self.bot_type,
            platform=self.platform,
            level=SessionLevel(self.level),
            id1=self.id1 or None,
            id2=self.id2 or None,
            id3=self.id3 or None,
        )

    @staticmethod
    def filter_statement(
        session: Session,
        id_type: Union[int, SessionIdType],
        *,
        include_platform: bool = True,
        include_bot_type: bool = True,
        include_bot_id: bool = True,
    ) -> List[ColumnElement[bool]]:
        id_type = min(max(id_type, 0), SessionIdType.GROUP_USER)

        if session.level == SessionLevel.LEVEL0:
            id_type = 0
        elif session.level == SessionLevel.LEVEL1:
            id_type = int(bool(id_type))
        elif session.level == SessionLevel.LEVEL2:
            id_type = (id_type & 1) | (int(bool(id_type >> 1)) << 1)
        elif session.level == SessionLevel.LEVEL3:
            pass

        include_id1 = bool(id_type & 1)
        include_id2 = bool((id_type >> 1) & 1)
        include_id3 = bool((id_type >> 2) & 1)

        whereclause: List[ColumnElement[bool]] = []
        if include_bot_id:
            whereclause.append(SessionModel.bot_id == session.bot_id)
        if include_bot_type:
            whereclause.append(SessionModel.bot_type == session.bot_type)
        if include_platform:
            whereclause.append(SessionModel.platform == session.platform)
        if include_id1:
            whereclause.append(SessionModel.id1 == (session.id1 or ""))
        if include_id2:
            whereclause.append(SessionModel.id2 == (session.id2 or ""))
        if include_id3:
            whereclause.append(SessionModel.id3 == (session.id3 or ""))
        return whereclause


async def get_or_add_session(session: Session) -> int:
    async with get_session() as db_session:
        if persist_id := (
            await db_session.scalars(
                select(SessionModel.id)
                .where(SessionModel.bot_id == session.bot_id)
                .where(SessionModel.bot_type == session.bot_type)
                .where(SessionModel.platform == session.platform)
                .where(SessionModel.level == session.level.value)
                .where(SessionModel.id1 == (session.id1 or ""))
                .where(SessionModel.id2 == (session.id2 or ""))
                .where(SessionModel.id3 == (session.id3 or ""))
            )
        ).one_or_none():
            return persist_id

    async with get_session() as db_session:
        session_model = SessionModel(
            bot_id=session.bot_id,
            bot_type=session.bot_type,
            platform=session.platform,
            level=session.level.value,
            id1=session.id1 or "",
            id2=session.id2 or "",
            id3=session.id3 or "",
        )
        db_session.add(session_model)
        await db_session.commit()
        await db_session.refresh(session_model)
        return session_model.id


async def get_session_by_id(sid: int) -> Session:
    async with get_session() as db_session:
        if session_model := (
            await db_session.scalars(select(SessionModel).where(SessionModel.id == sid))
        ).one_or_none():
            return session_model.session
    raise ValueError(f"Session with id '{sid}' not found")
