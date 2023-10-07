import pytest
from nonebot import require
from nonebug import NONEBOT_INIT_KWARGS, App
from sqlalchemy import delete


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "sqlalchemy_database_url": "sqlite+aiosqlite:///:memory:",
        "alembic_startup_check": False,
    }


@pytest.fixture
async def app(app: App):
    require("nonebot_plugin_session_orm")

    from nonebot_plugin_orm import get_session, init_orm

    await init_orm()

    yield app

    from nonebot_plugin_session_orm import SessionModel

    async with get_session() as db_session:
        await db_session.execute(delete(SessionModel))
