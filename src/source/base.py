import asyncio
from aioreactive import AsyncSubject
from contextlib import AbstractAsyncContextManager
from typing import (
    Any,
    AsyncIterator,
    Type,
    TypeVar,
    overload,
    Generic,
    Callable,
    NoReturn,
    Coroutine,
)
from collections.abc import AsyncIterable
from db.models import ModelBase
from loguru import logger
from aioreactive import AsyncIteratorObserver
from typing_extensions import Self

T = TypeVar("T", bound=ModelBase)


class DataSource(Generic[T], AsyncIterable[T], AbstractAsyncContextManager):
    def __init__(
        self,
        schema: Type[T],
        receive_data: Callable[[Self], Coroutine[Any, Any, NoReturn | None]]
        | None = None,
    ) -> None:
        self.schema = schema
        self.stream = AsyncSubject[T]()
        self.task: asyncio.Task | None = None
        self.receive_data_forever = receive_data

    @overload
    async def add(self, data: T) -> T:
        ...

    @overload
    async def add(self, data: str | bytes) -> T:
        ...

    async def add(self, data: str | bytes | T):
        match data:
            case str() | bytes():
                logger.info(f"received data {data!r}")
                a = self.schema.from_str(data)
                await self.stream.asend(a)
                return a
            case _:
                await self.stream.asend(data)
                return data

    def open_connection(self):
        if self.receive_data_forever:
            self.task = asyncio.create_task(self.receive_data_forever(self))

    def close_connection(self):
        if self.task:
            self.task.cancel()
            self.task = None

    async def __aenter__(self):
        self.open_connection()
        return self

    async def __aexit__(self, *args) -> bool | None:
        self.close_connection()

    def __aiter__(self) -> AsyncIterator[T]:
        return AsyncIteratorObserver(self.stream)
