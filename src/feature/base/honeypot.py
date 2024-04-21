import contextlib
from typing import (
    Protocol,
    ClassVar,
    Type,
    TypeVar,
    cast,
    runtime_checkable,
)
from collections import defaultdict
from typing_extensions import override
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from db.models import Base
from functools import cache
from db.crud import CRUDWithSession, CRUDBase
from ..utils import inject_constructor, lifespan_scope, WebsocketManager
from fastapi_injector import Injected, request_scope
from sqlmodel.ext.asyncio.session import AsyncSession
from injector import Binder, ClassProvider, singleton
from source.base import DataSource
from logger import Logger
from .mixin.base import Mixin

TModel = TypeVar("TModel", bound=Base, covariant=True)
TDBModel = TypeVar("TDBModel", bound=Base)

TCRUD = TypeVar("TCRUD", bound=CRUDWithSession)


class Route:
    def __init__(self, honeypot: Type["Honeypot"]) -> None:
        self.honeypot = honeypot

    def configure_get_attacks(self):
        @self.honeypot.router.get(
            "/",
            response_model=list[self.honeypot._ResponseModel],  # type: ignore
        )
        async def default_get_attacks(
            offset: int = 0,
            limit: int = 10,
            crud: CRUDWithSession[TDBModel] = Injected(
                self.honeypot.CRUD  # type: ignore
            ),
        ) -> list[TDBModel]:
            return [attack async for attack in crud.get(offset, limit)]

        return default_get_attacks

    def configure_create_attack(self):
        @self.honeypot.router.post(
            "/",
            response_model=self.honeypot._ResponseModel,  # type: ignore
        )
        async def default_create_attack(
            attack: self.honeypot.attack_model,
            source: DataSource[TDBModel] = Injected(
                self.honeypot.Source  # type: ignore
            ),
        ) -> TDBModel:
            return await source.add(cast(TDBModel, attack))

        return default_create_attack

    def configure_send_attack_with_websocket(self):
        """
        配置一个实时发送attacks的websocket路由
        """

        @self.honeypot.router.websocket("/ws")
        async def _send_attack_info(
            websocket: WebSocket,
            subscribe: WebsocketManager[TDBModel] = Injected(
                self.honeypot.Websocket  # type: ignore
            ),
        ):
            await websocket.accept()

            with subscribe(websocket):
                with contextlib.suppress(WebSocketDisconnect):
                    while True:
                        # 只需要捕获断连错误，不用处理客户端发来的文本
                        await websocket.receive_text()

        return _send_attack_info


@runtime_checkable
class _Honeypot(Protocol[TModel, TDBModel]):
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
    attack_model: ClassVar[Type[Base]]
    """
    因为[PEP 526](https://www.python.org/dev/peps/pep-0526/#class-and-instance-variable-annotations)的限制，
    ClassVar内不能有泛型，没办法做静态检查，所以这里一定要确保`database_model`的值和泛型的类型`Type[T]`一致
    """
    db_model: ClassVar[Type[Base]]
    """
    表示数据库表的一个类，通常只需要继承上面的`attack_model`并且加一个`id`字段就可以
    >>> from sqlmodel import Field
    ... 
    >>> class ModelInDB(YourModel, table=True):
    >>>     id: int | None = Field(default=None, primary_key=True, unique=True)

    """

    @classmethod
    @property
    @cache
    def _ResponseModel(cls: Type["Honeypot"]):
        class ModelWithId(cls.attack_model):
            id: int

        return ModelWithId

    @classmethod
    def configure(cls):
        cls.configure_honeypot()

    @classmethod
    def configure_honeypot(cls):
        route = Route(cls)

        cls.configure_routes(route)

    @staticmethod
    def configure_routes(route: "Route") -> None:
        """
        在这里配置这个蜜罐的fastapi路由
        """
        ...

    @classmethod
    @property
    @cache
    def CRUD(cls: Type["Honeypot"]):
        """
        生成的这个蜜罐的数据库CRUD类
        """

        @request_scope
        @inject_constructor
        class _CRUD(CRUDWithSession[cls.db_model]):
            crud = CRUDBase(cls.db_model)
            session: AsyncSession

        return _CRUD

    @staticmethod
    async def receive_data_forever(source: DataSource[TDBModel]):
        """
        如果这个蜜罐有一些需要实时监听的数据，就在这里进行监听，
        需要调用`source.add()`方法把接收到的数据格式化成`TModel`，然后放入`source.stream`中
        """

    @classmethod
    @property
    @cache
    def Source(cls: Type["Honeypot"]):
        """
        生成的这个蜜罐的`DataSource`类，这个类里面有一个`stream`流，可以订阅这个流，在蜜罐每次接收一个attack时收到这个attack
        """

        @lifespan_scope
        @inject_constructor
        class _Source(DataSource[cls.db_model]):
            schema = cls.db_model
            logger: Logger
            crud: CRUDWithSession[cls.db_model]

            async def receive_data_forever(self):
                return await cls.receive_data_forever(self)

        return _Source

    @classmethod
    @property
    @cache
    def Websocket(cls):
        """
        用于管理websocket连接的类
        """

        @singleton
        @inject_constructor
        class _Websocket(WebsocketManager):
            source: cls.Source  # type: ignore
            logger: Logger

        return _Websocket

    @classmethod
    def bind_class_types(cls: Type["Honeypot"], binder: Binder):
        binder.bind(
            CRUDWithSession[cls.db_model],
            ClassProvider(cls.CRUD),  # type: ignore
            scope=request_scope,
        )
        binder.bind(
            DataSource[cls.db_model],
            ClassProvider(cls.Source),  # type: ignore
            scope=request_scope,
        )
        binder.bind(
            WebsocketManager[cls.db_model],
            ClassProvider(cls.Websocket),  # type: ignore
        )


class MixinConfiger(type(Protocol)):
    _mixins: ClassVar[dict[str, list[Type[Mixin]]]] = defaultdict(list)

    def __new__(
        cls,
        __name,
        __bases,
        __namespace,
    ):
        for b in __bases:
            if issubclass(b, Mixin):
                cls._mixins[__name].append(b)
                # b.configure_mixin(cls)

        return super().__new__(cls, __name, __bases, __namespace)


class Honeypot(_Honeypot[TModel, TDBModel], Protocol, metaclass=MixinConfiger):
    @override
    @classmethod
    def configure(cls):
        for mixin in cls._mixins[cls.__name__]:
            mixin.configure_mixin(cast(Type[Mixin], cls))
        return super().configure()
