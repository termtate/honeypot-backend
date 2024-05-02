from contextlib import contextmanager
from expression import pipe
from fastapi import WebSocket
from pydantic import RootModel
from source.base import DataSource
from loguru import logger
from core import setting
import aioreactive as rx
import asyncio
from typing import TypeVar, Generic
from db.models import ModelBase

T = TypeVar("T", bound=ModelBase)


def buffer(interval: int):
    """
    每隔一定的时间间隔分组发送收到的数据

    1 -> 2 -> 3 -> 4 -> 5 -> ...
            |         |
            |         |
          [1, 2]    [3, 4]
    """

    async def _buffer(
        stream: rx.AsyncObservable[T],
    ) -> rx.AsyncObservable[list[T]]:
        s = rx.AsyncSubject[list[T]]()
        buffer: list[T] = []

        async def timer():
            while True:
                await asyncio.sleep(interval)
                if buffer:
                    await s.asend(buffer)
                    buffer.clear()

        task = asyncio.create_task(timer())

        async def asend(v):
            buffer.append(v)

        async def aclose():
            task.cancel()

        await stream.subscribe_async(
            rx.AsyncAnonymousObserver(asend, aclose=aclose)
        )

        return s

    return _buffer


class WebsocketManager(Generic[T]):
    def __init__(self, source: DataSource[T]) -> None:
        self.source = source

    async def receive(self, websocket: WebSocket):
        buffered_stream = await pipe(
            self.source.stream,
            buffer(setting.WEBSOCKET_BUFFER_SEND_INTERVAL.seconds),
        )

        async for attacks in rx.AsyncIteratorObserver(buffered_stream):
            text = str(
                [RootModel[T](attack).model_dump_json() for attack in attacks]
            )
            await websocket.send_text(text)
            logger.info(f"send attack to {websocket}")

    @contextmanager
    def __call__(self, websocket: WebSocket):
        task = asyncio.create_task(self.receive(websocket))
        try:
            yield
        finally:
            task.cancel()
