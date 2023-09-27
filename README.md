# nonebot-plugin-session-orm

为 [session](https://github.com/noneplugin/nonebot-plugin-session) 提供数据库模型及存取方法


### 安装

- 使用 nb-cli

```
nb plugin install nonebot_plugin_session_orm
```

- 使用 pip

```
pip install nonebot_plugin_session_orm
```

### 使用

```python
from nonebot import require

require("nonebot_plugin_session_orm")

from nonebot_plugin_orm import get_scoped_session
from nonebot_plugin_session import EventSession
from nonebot_plugin_session_orm import get_or_add_session_model

@matcher.handle()
async def handle(event_session: EventSession):
    Session = get_scoped_session()
    async with Session() as db_session:
        session_model = await get_or_add_session_model(event_session, db_session)
```
