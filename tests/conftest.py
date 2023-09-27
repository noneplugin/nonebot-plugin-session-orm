from contextlib import suppress

import pytest
from nonebot import require
from nonebug import NONEBOT_INIT_KWARGS, App
from sqlalchemy import delete


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "sqlalchemy_database_url": "sqlite+aiosqlite:///:memory:"
    }


@pytest.fixture
async def app(app: App):
    require("nonebot_plugin_session_orm")

    from nonebot_plugin_orm import get_scoped_session, greenlet_spawn, orm

    Session = get_scoped_session()

    with suppress(SystemExit):
        await greenlet_spawn(orm, ["upgrade"])

    yield app

    from nonebot_plugin_session_orm import SessionModel

    async with Session() as session, session.begin():
        await session.execute(delete(SessionModel))
