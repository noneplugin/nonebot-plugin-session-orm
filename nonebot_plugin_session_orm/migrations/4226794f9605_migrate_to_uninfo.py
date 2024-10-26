"""migrate_to_uninfo

迁移 ID: 4226794f9605
父迁移: 25c9e3af1647
创建时间: 2024-10-26 16:42:44.116144

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from nonebot import logger
from sqlalchemy import Connection
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

revision: str = "4226794f9605"
down_revision: str | Sequence[str] | None = "25c9e3af1647"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = "6f1edf4c1af7"


def _platform_to_scope(platform: str, id1: str) -> str:
    from nonebot_plugin_session.const import SupportedPlatform
    from nonebot_plugin_uninfo import SupportScope

    if platform == SupportedPlatform.console:
        return SupportScope.console
    elif platform == SupportedPlatform.discord:
        return SupportScope.discord
    elif platform == SupportedPlatform.dodo:
        return SupportScope.dodo
    elif platform == SupportedPlatform.feishu:
        return SupportScope.feishu
    elif platform == SupportedPlatform.kaiheila:
        return SupportScope.kook
    elif platform == SupportedPlatform.qq:
        if len(id1) > 12:
            return SupportScope.qq_api
        return SupportScope.qq_client
    elif platform == SupportedPlatform.qqguild:
        return SupportScope.qq_guild
    elif platform == SupportedPlatform.telegram:
        return SupportScope.telegram
    else:
        return SupportScope.unknown


def _level_to_scene(
    level: int, id1: str, id2: str, id3: str
) -> tuple[int, str, int, str]:
    from nonebot_plugin_session import SessionLevel
    from nonebot_plugin_uninfo import SceneType

    scene_type = -1
    scene_id = ""
    parent_scene_type = -1
    parent_scene_id = ""

    if level == SessionLevel.PRIVATE:
        scene_type = SceneType.PRIVATE
        scene_id = id1
    elif level == SessionLevel.GROUP:
        scene_type = SceneType.GROUP
        scene_id = id2
    elif level == SessionLevel.CHANNEL:
        if not id2:
            scene_type = SceneType.GUILD
            scene_id = id3
        else:
            scene_type = SceneType.CHANNEL_TEXT
            scene_id = id2
            parent_scene_type = SceneType.GUILD
            parent_scene_id = id3

    return scene_type, scene_id, parent_scene_type, parent_scene_id


def _read_session_data(conn: Connection) -> dict[int, dict]:
    Base = automap_base()
    Base.prepare(autoload_with=conn)
    SessionModel = Base.classes.nonebot_plugin_session_orm_sessionmodel

    session_model_dict: dict[int, dict] = {}

    with Session(conn) as db_session:
        session_models = db_session.scalars(sa.select(SessionModel)).all()
        for session_model in session_models:
            bot_id = session_model.bot_id
            bot_type = session_model.bot_type
            platform = session_model.platform
            level = session_model.level
            id1 = session_model.id1
            id2 = session_model.id2
            id3 = session_model.id3

            scope = _platform_to_scope(platform, id1)
            scene_type, scene_id, parent_scene_type, parent_scene_id = _level_to_scene(
                level, id1, id2, id3
            )

            session_model_dict[session_model.id] = {
                "self_id": bot_id,
                "adapter": bot_type,
                "scope": scope,
                "scene_id": scene_id,
                "scene_type": scene_type,
                "scene_data": {},
                "parent_scene_id": parent_scene_id,
                "parent_scene_type": parent_scene_type,
                "parent_scene_data": None,
                "user_id": id1,
                "user_data": {},
                "member_data": None,
            }
    return session_model_dict


def _write_uninfo_data(
    conn: Connection, session_model_dict: dict[int, dict]
) -> dict[int, int]:
    Base = automap_base()
    Base.prepare(autoload_with=conn)
    SessionModel = Base.classes.nonebot_plugin_uninfo_sessionmodel

    id_map: dict[int, int] = {}
    session_key_id_map: dict[tuple, int] = {}

    with Session(conn) as db_session:
        session_models = db_session.scalars(sa.select(SessionModel)).all()
        for session_model in session_models:
            session_key = (
                session_model.self_id,
                session_model.adapter,
                session_model.scope,
                session_model.scene_id,
                session_model.scene_type,
                session_model.parent_scene_id,
                session_model.parent_scene_type,
                session_model.user_id,
            )
            session_key_id_map[session_key] = session_model.id

        for session_id, uninfo_data in session_model_dict.items():
            session_key = (
                uninfo_data["self_id"],
                uninfo_data["adapter"],
                uninfo_data["scope"],
                uninfo_data["scene_id"],
                uninfo_data["scene_type"],
                uninfo_data["parent_scene_id"],
                uninfo_data["parent_scene_type"],
                uninfo_data["user_id"],
            )
            if session_key in session_key_id_map:
                id_map[session_id] = session_key_id_map[session_key]
                continue

            session_model = SessionModel(**uninfo_data)
            db_session.add(session_model)
            db_session.commit()
            db_session.refresh(session_model)
            uninfo_id = session_model.id
            id_map[session_id] = uninfo_id
            session_key_id_map[session_key] = uninfo_id

    return id_map


def _write_id_map(conn: Connection, id_map: dict[int, int]) -> None:
    Base = automap_base()
    Base.prepare(autoload_with=conn)
    IdMap = Base.classes.nonebot_plugin_session_orm_sessiontouninfomap

    with Session(conn) as db_session:
        for session_id, uninfo_id in id_map.items():
            db_session.add(IdMap(session_id=session_id, uninfo_id=uninfo_id))
        db_session.commit()


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    session_model_dict = _read_session_data(conn)
    if not session_model_dict:
        return
    logger.info("session-orm: 正在将数据迁移至 uninfo...")
    id_map = _write_uninfo_data(conn, session_model_dict)
    _write_id_map(conn, id_map)
    logger.info("session-orm: 迁移完成")
    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
