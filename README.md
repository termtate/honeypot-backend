# honeypot-backend

All Async Web App with Fastapi + SQLAlchemy 2.0 + Injector + aioreactive


## before run

- install [rye](https://rye-up.com/guide/installation/)
- install postgresql


## run project

1. `rye sync`（第一次运行项目时输入）
2. `rye run python src/create_tables.py`（创建数据库表）（第一次运行项目时输入）
3. `rye run python src/pre_start.py`（测试数据库连接）
4. `rye run server` 运行服务器
5. http://127.0.0.1:8000/docs 查看openapi文档


## develop
- 建议使用vscode和配套python扩展进行开发
- 运行`rye run lint`格式化代码


## 架构描述

### 项目特点

1. 全部使用协程保证并发性
2. 使用[aioreactive](https://github.com/dbrattli/aioreactive)提供异步流的响应式编程支持
3. 使用[injector](https://github.com/python-injector/injector)提供依赖注入支持
4. fastapi提供对外的网络接口
5. sqlalchemy提供数据库的orm操作
6. rye管理python版本、项目依赖、脚本运行
7. 用ruff和yapf进行代码格式化


### 整体架构

项目从整体上可以划分为3层：
- common层，包含项目最基本的设置和logger模块，供其他所有模块使用
- 用来给实际业务提供功能和整体框架的基础层，基础层实现了主要的框架逻辑，具体的细节需要通过继承子类的方式，由业务层自己实现。基础层包含db, schema和source
- 业务层，用来描述实际接收攻击信息的解析方法、解析之后的数据类、数据库的表以及存储逻辑、fastapi网络接口等功能。
    > 这里的业务具体指处理每一种蜜罐传来的信息、保存这些信息至数据库、进行数据分析、提供网络接口等工作

![整体架构示意图](images/architecture.svg)


业务层中每一个具体业务的大部分功能可以通过继承基础层中的数种Base类来获得，所以基本上对于每一个业务，只需要书写以下代码就能拥有基础功能：
1. 写一个描述蜜罐传来的信息的数据类，并且编写一个方法来把传来的信息转换为这个数据类
2. 写一个sqlalchemy的orm类，来描述用来存储传来信息的数据库的表
  
剩下的代码基本上复制粘贴就可以  
具体的步骤在下面的[增加一个新模块的步骤](#增加一个新模块的步骤)

### 单个蜜罐内的架构

![蜜罐架构示意图](images/honeypot_arch.svg)
> source产生attack的来源也可以不只是socket，只要在内部调用`self.stream.asend()`方法把attack放入stream就可以


## 增加一个新模块的步骤

假设增加的新数据模块名为honeypot，socket传来的每次信息是json格式的字符串，内容如下：
```json
{
    "content": "...",
    "time": "2023-01-01T00:00:00"
}
```

首先需要在feature文件夹里新建一个文件夹honeypot，这个文件夹内需要包括的内容有：
- 继承[db.model.Base类](src/db/models/base.py#6)的orm类，项目程序会在运行时根据这个orm类生成数据库的一张表   
    `feature/honeypot/model.py`
    
    ```py
    from db.models import Base
    from sqlalchemy.orm import Mapped
    from datetime import datetime


    class AttackOrm(Base):
        __tablename__ = "honeypot"

        content: Mapped[str]
        time: Mapped[datetime]
        
    ```
    > 对于orm类的创建可以查看sqlalchemy文档 https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#declarative-mapping
- 实现了[schema.base.Schema协议](src/schema/base.py#5)的schema类。这个类需要把socket传来的json的字段表示为数据类，并且实现`from_str()`方法，用来把一段字符串/字节流解析为这个schema类
    `feature/honeypot/schema.py`

    ```py
    from pydantic import BaseModel, ConfigDict
    from datetime import datetime


    class AttackSchema(BaseModel):
        model_config = ConfigDict(from_attributes=True) 

        content: str
        time: datetime

        @classmethod
        def from_str(cls, content):
            return cls.model_validate_json(content)
    ```
    这个例子的schema类使用了[pydantic的BaseModel类](https://docs.pydantic.dev/latest/concepts/models/)作为数据的声明式验证  
    schema类除了验证socket数据流之外，还可以作为fastapi接口的模式；该类的属性在大部分情况下和orm类应该是一致的
    > 对于fastapi接口模式的详细schema设置可以查看fastapi文档 https://fastapi.tiangolo.com/zh/tutorial/response-model/
- 继承 [db.crud.base.CRUDWithSession类](src/db/crud/base.py#44)的CRUD类   
    `feature/honeypot/crud.py`

    ```py
    from db.crud import CRUDWithSession, CRUDBase
    from .model import AttackOrm
    from .schema import AttackSchema
    from fastapi_injector import request_scope
    from sqlalchemy.ext.asyncio import AsyncSession
    from ..utils import inject_constructor


    @request_scope
    @inject_constructor
    class CRUDAttack(CRUDWithSession[AttackSchema, AttackOrm]):
        crud = CRUDBase(AttackOrm)
        session: AsyncSession

    ```
    crud类用`request_scope`装饰表示该类的每个实例的生命周期只在一次fastapi请求中，对于每个不同的请求都会新建一个新的实例。这样做的原因是因为`session`的生命周期需要对应于fastapi请求（在请求开始时建立session，请求结束时提交并关闭session），所以每一次请求都会新建一个crud，获取一个新的session  
    `@inject_constructor`表示该类可以像`dataclass`一样声明构造参数，并且`__init__`方法被`injector.inject`修饰，从而能够被`injector`依赖注入框架调用

- 继承 [feature.utils.socket.SocketSource类](src/feature/utils/socket.py#57)的source类
    `feature/honeypot/source.py`

    ```py
    from .schema import AttackSchema
    from logger import Logger
    from schema.socket import Socket
    from ..utils import lifespan_scope, SocketSource, inject_constructor


    @lifespan_scope
    @inject_constructor
    class HoneypotSource(SocketSource[AttackSchema]):
        schema = AttackSchema
        socket = Socket(ip="localhost", port=1234)
        logger: Logger

    ```
    填入自己定义的schema类和socket地址即可   
    `@lifespan_scope`的具体含义可以查看[这里](src/feature/utils/lifespan_scope.py#11)
- 按照fastapi的接口书写方式定义网络接口  
    `feature/honeypot/endpoint.py`

    ```py
    from fastapi import APIRouter
    from fastapi_injector import Injected
    from .crud import CRUDAttack


    router = APIRouter()

    @router.get("/")
    async def get_attacks(
        offset: int = 0,
        limit: int = 10,
        crud: CRUDAttack = Injected(CRUDAttack),  # 需要用到之前的crud类的时候要用Injected
    ):
        return [attack async for attack in crud.get(offset, limit)]

    ```
- 编写一个函数，用来在`HoneypotSource`接收到消息时保存到数据库   
    `feature/honeypot/__init__.py`

    ```py
    from ..utils import store_attack, lifespan_scope
    from injector import Injector
    from .source import HoneypotSource
    from .crud import CRUDAttack


    @lifespan_scope.on_startup
    def store_attacks_to_db(injector: Injector):
        return store_attack(HoneypotSource, CRUDAttack)(injector)

    ```
    这个函数用来在fastapi启动时开始收集`HoneypotSource.stream`并把每个`attack`保存到数据库  
    **注意：被`@lifespan_scope.on_startup`修饰的函数要定义在`__init__.py`里，或者显式在main.py里导入**，因为python代码需要被导入才能运行，如果在fastapi启动前这个函数（所在的文件）没有被引用到的话装饰器就不会运行，也就不会执行启动逻辑

增加上述代码以后，`honeypot`包的结构应该是：
```
feature
├─honeyd
|   ├─__init__.py
|   ├─crud.py
|   ├─endpoint.py
|   ├─model.py
|   ├─schema.py
|   └─source.py
```

可选项：
- 如果网页有实时显示攻击数据的需求，则需要新建`WebsocketManager`类并且增加websocket端口
  - `feature/honeypot/websocket.py`   
    ```py
    from ..utils import WebsocketManager, inject_constructor
    from .schema import AttackSchema
    from injector import singleton
    from .source import HoneypotSource
    from logger import Logger
    from core import Settings


    @singleton
    @inject_constructor
    class HoneypotWebsocket(WebsocketManager[AttackSchema]):
        source: HoneypotSource
        logger: Logger
        setting: Settings
    ```
  - `feature/honeypot/endpoint.py`  
    ```py
    from .websocket import HoneypotWebsocket
    import contextlib
    from fastapi import WebSocket, WebSocketDisconnect

    ...

    @router.websocket("/ws")
    async def send_attack_info(
        websocket: WebSocket,
        subscribe: HoneypotWebsocket = Injected(HoneypotWebsocket)
    ):
        await websocket.accept()

        with subscribe(websocket):
            with contextlib.suppress(WebSocketDisconnect):
                while True:
                    await websocket.receive_text()
    ```

模块代码写完后，在`feature/api.py`注册模块的`router`。`router`在被注册后才能使用
```py
from .honeypot.endpoint import router as honeypot_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(honeypot_router, prefix="/honeypot_attacks", tags=["honeypot"])

```

在`create_tables.py`与`drop_tables.py`中导入`feature/honeypot/model.py:AttackOrm`，因为创建和删除表的时候会查找所有继承`Base`类的子类，然后根据这些子类进行创建和删除表的工作，所以要提前导入`AttackOrm`类，让`Base`类能够找到它。
```py
# noqa: F401 用来告诉代码格式化工具不要删掉这个没有用到的导入
from feature.honeypot.model import AttackOrm as honeypot_attack  # noqa: F401
...
```

运行`rye run python src/create_tables.py`创建表  
运行`rye run server`运行服务


## 参考项目

- https://github.com/rhoboro/async-fastapi-sqlalchemy/tree/main Async Web API with FastAPI + SQLAlchemy 2.0