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

from nonebot_plugin_session import EventSession
from nonebot_plugin_session_orm import get_session_persist_id, get_session_by_persist_id

@matcher.handle()
async def handle(session: EventSession):
    persist_id = await get_session_persist_id(session) # 存储 session，返回 persist_id
    session_loaded = await get_session_by_persist_id(persist_id) # 通过 persist_id 获取 session
```
