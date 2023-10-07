from nonebug.app import App
from sqlalchemy import select

from .utils import assert_session


async def test_add_and_filter_session(app: App):
    from nonebot_plugin_orm import get_session
    from nonebot_plugin_session import Session as EventSession
    from nonebot_plugin_session import SessionLevel

    from nonebot_plugin_session_orm import (
        SessionModel,
        get_or_add_session,
        get_session_by_id,
    )

    event_session = EventSession(
        bot_id="2233",
        bot_type="OneBot V11",
        platform="qq",
        level=SessionLevel.LEVEL2,
        id1="3344",
        id2="1122",
        id3=None,
    )

    sid = await get_or_add_session(event_session)
    assert sid != 0

    event_session = await get_session_by_id(sid)
    assert_session(
        event_session,
        bot_id="2233",
        bot_type="OneBot V11",
        platform="qq",
        level=SessionLevel.LEVEL2,
        id1="3344",
        id2="1122",
        id3=None,
    )

    async with get_session() as db_session:
        statement = select(SessionModel).where(
            SessionModel.bot_id == "2233",
            SessionModel.level == SessionLevel.LEVEL2,
            SessionModel.id2 == "1122",
        )
        session_models = (await db_session.scalars(statement)).all()
        assert session_models
        assert len(session_models) == 1
        session_model = session_models[0]
        assert_session(
            session_model.session,
            bot_id="2233",
            bot_type="OneBot V11",
            platform="qq",
            level=SessionLevel.LEVEL2,
            id1="3344",
            id2="1122",
            id3=None,
        )
