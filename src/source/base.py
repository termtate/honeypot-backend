import asyncio
from aioreactive import AsyncSubject
from contextlib import AbstractContextManager
from typing import AsyncIterator, Protocol, Type, TypeVar, overload
from collections.abc import AsyncIterable
from db.models import Base
from logger import Logger
from aioreactive import AsyncIteratorObserver
from db.crud import CRUDWithSession

T = TypeVar("T", bound=Base)


class DataSource(AsyncIterable[T], AbstractContextManager, Protocol[T]):
    schema: Type[T]
    stream: AsyncSubject[T] = AsyncSubject()
    task: asyncio.Task | None = None
    logger: Logger
    crud: CRUDWithSession[T]

    async def receive_data_forever(self):
        """
        循环接收数据，在方法中调用self.add()将数据保存到流中
        """
        ...

    @overload
    async def add(self, data: T) -> T:
        ...

    @overload
    async def add(self, data: str | bytes) -> T:
        ...

    async def add(self, data: str | bytes | T):
        match data:
            case str() | bytes():
                self.logger.info(f"received data {data!r}")
                a = self.schema.from_str(data)
                await self.stream.asend(a)
                await self.crud.create(a)
                return a
            case _:
                await self.stream.asend(data)
                await self.crud.create(data)
                return data

    def open_connection(self):
        self.task = asyncio.create_task(self.receive_data_forever())

    def close_connection(self):
        assert self.task is not None, "还未打开连接"
        self.task.cancel()
        self.task = None

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, __exc_type, __exc_value, __traceback) -> bool | None:
        self.close_connection()

    def __aiter__(self) -> AsyncIterator[T]:
        return AsyncIteratorObserver(self.stream)
