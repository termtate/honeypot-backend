import contextlib
from typing import (
    Protocol,
    ClassVar,
    Type,
    TypeVar,
    runtime_checkable,
    Generic,
)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from db.models import ModelBase
from functools import cache
from db.crud import CRUDBase
from db import AsyncSession
from ..utils import WebsocketManager
from fastapi_injector import Injected
from source.base import DataSource
from schema.base import Schema
from .mixin import DockerMixin, MainStream
from contextlib import AbstractAsyncContextManager
from .lifespan_context import LifespanContext

TModel = TypeVar("TModel", bound=Schema)
TDBModel = TypeVar("TDBModel", bound=ModelBase)


class Route(Generic[TModel, TDBModel]):
    def __init__(self, honeypot: Type["Honeypot[TModel, TDBModel]"]) -> None:
        self.honeypot = honeypot

    def configure_get_attacks(self):
        @self.honeypot.router.get(
            "/",
            response_model=list[self.honeypot.db_model],
        )
        async def default_get_attacks(
            offset: int = 0,
            limit: int = 10,
            session: AsyncSession = Injected(AsyncSession),
        ) -> list[TDBModel]:
            return [
                attack
                async for attack in self.honeypot.crud.get(
                    session, offset, limit
                )
            ]

        return default_get_attacks

    def configure_create_attack(self):
        @self.honeypot.router.post("/", response_model=self.honeypot.db_model)
        async def default_create_attack(
            attack: self.honeypot.attack_model,
            session: AsyncSession = Injected(AsyncSession),
        ) -> TDBModel:
            a = self.honeypot.db_model.model_validate(attack)
            m = await self.honeypot.crud.create(session, a)
            return await self.honeypot.source.add(m)

        return default_create_attack

    def configure_send_attack_with_websocket(self):
        """
        配置一个实时发送attacks的websocket路由
        """

        @self.honeypot.router.websocket("/ws")
        async def _send_attack_info(
            websocket: WebSocket,
        ):
            await websocket.accept()

            with self.honeypot.websocket_manager(websocket):
                with contextlib.suppress(WebSocketDisconnect):
                    while True:
                        # 只需要捕获断连错误，不用处理客户端发来的文本
                        await websocket.receive_text()

        return _send_attack_info


@runtime_checkable
class Honeypot(LifespanContext, Protocol[TModel, TDBModel]):
    """
    因为编写一个蜜罐，所需的代码大多是相同的，所以编写了这个类，用来动态生成蜜罐的大部分功能

    通过继承这个类并编写一点配置后，这个类能够生成与这个蜜罐对应的：
    1. `DataSource`类: `Honeypot.Source`
    2. `CRUDWithSession`类: `Honeypot.CRUD`
    3. `WebsocketManager`类: `Honeypot.Websocket`
    4. 数据库增、查的fastapi路由
    4. websocket fastapi路由，可以在蜜罐新增一条攻击后把攻击信息发给websocket的订阅者

    **不要实例化这个类（的子类）**

    写完这个类以后，要记得去`__init__.py`的`all_honeypots`列表里加上新增的类

    这个类的用法：
    - 使用injector获取蜜罐相关类的实例：

        >>> @inject
        >>> async def get_attacks(source: DataSource[MyDBModel]):
        >>>     async for attack in source:
        >>>         print(attack)

        >>> @inject
        >>> async def get_attacks(crud: CRUDWithSession[MyDBModel]):
        >>>     return await crud.get(limit=10)
        可以直接使用`DataSource[MyDBModel]`等表示相关类的类型并用`@inject`获取到，因为`Honeypot`类已经完成了类型的绑定工作
    - 或者可以手动初始化类（不推荐）：

        >>> source = MyHoneypot.Source(schema=..., logger=...)

    这个类只负责对于大部分重复样板代码的动态生成，如果要实现的蜜罐有其他定制化需求，可以考虑手动编写相关的实现类
    """

    router: ClassVar[APIRouter]
    """
    创建一个属于这个蜜罐的fastapi的router，可以在这里配置这个router的前缀等
    """
    attack_model: ClassVar[Type[TModel]]  # type: ignore

    db_model: ClassVar[Type[TDBModel]]  # type: ignore
    """
    表示数据库表的一个类，通常只需要继承上面的`attack_model`并且加一个`id`字段就可以
    >>> from sqlmodel import Field
    ... 
    >>> class ModelInDB(YourModel, table=True):
    >>>     id: int | None = Field(default=None, primary_key=True, unique=True)

    """

    docker_config: ClassVar[DockerMixin | None] = None
    main_stream_config: ClassVar[MainStream[TDBModel] | None] = None

    lifespan_events: ClassVar[set[AbstractAsyncContextManager]]

    def __init_subclass__(cls) -> None:
        cls.lifespan_events = set()

    @classmethod
    @property
    @cache
    def crud(cls) -> CRUDBase[TDBModel]:
        return CRUDBase(cls.db_model)

    @classmethod
    def configure(cls):
        route = Route(cls)

        cls.configure_routes(route)

    @staticmethod
    def configure_routes(route: "Route") -> None:
        """
        在这里配置这个蜜罐的fastapi路由
        """
        ...

    @staticmethod
    async def receive_data_forever(source: DataSource[TDBModel]):
        """
        如果这个蜜罐有一些需要实时监听的数据，就在这里进行监听，
        需要调用`source.add()`方法把接收到的数据格式化成`TModel`，然后放入`source.stream`中
        """

    @classmethod
    @property
    @cache
    def source(cls: Type["Honeypot"]) -> DataSource[TDBModel]:
        """
        生成的这个蜜罐的`DataSource`类，这个类里面有一个`stream`流，可以订阅这个流，在蜜罐每次接收一个attack时收到这个attack
        """
        source = DataSource(
            cls.db_model, receive_data=cls.receive_data_forever
        )
        cls.lifespan_events.add(source)
        return source

    @classmethod
    @property
    @cache
    def websocket_manager(cls) -> WebsocketManager[TDBModel]:
        """
        用于管理websocket连接的类
        """

        return WebsocketManager(cls.source)
