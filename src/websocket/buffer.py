import aioreactive as rx
import asyncio
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")


def buffer(interval: int):
    """
    每隔一定的时间间隔分组发送收到的数据
    
    1 -> 2 -> 3 -> 4 -> 5 -> ...
            |         |
            |         |
          [1, 2]    [3, 4]
    """

    async def _buffer(
        stream: rx.AsyncObservable[T]
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