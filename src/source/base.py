import asyncio
from aioreactive import AsyncSubject
from contextlib import AbstractContextManager
from typing import Protocol, Type, TypeVar
from schema import Schema
from logger import Logger

T = TypeVar("T", bound=Schema)


class DataSource(AbstractContextManager, Protocol[T]):
    schema: Type[T]
    stream: AsyncSubject[T] = AsyncSubject()
    task: asyncio.Task | None = None
    logger: Logger

    async def receive_data_forever(self):
        """
        循环接收数据，在方法中调用self.stream.asend()将数据保存到流中
        """
        ...

    def add(self, content: str | bytes):
        self.logger.info(f"received data {content!r}")
        return self.stream.asend(self.schema.from_str(content))

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
