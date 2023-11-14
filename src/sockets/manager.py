from abc import ABC, abstractmethod
from schema import Attack, Socket
import asyncio
from injector import inject
from typing_extensions import override
from logger import Logger
from aioreactive import AsyncSubject, AsyncObservable
from contextlib import AbstractContextManager


class SocketsManager(ABC):
    @abstractmethod
    def get_attack_stream(self) -> AsyncObservable[Attack]:
        pass

    @abstractmethod
    def open_connections(self) -> None:
        pass

    @abstractmethod
    def close_connections(self) -> None:
        pass


class RealSocketsManager(SocketsManager, AbstractContextManager):
    """
    开启多个socket并同时接收数据，将接收的数据解析为`Attack`类并放入`self.stream` 可观察流 中 \n
    在使用时，需要订阅`stream`获取数据
    >>> from aioreactive import AsyncAnonymousObserver, AsyncIteratorObserver
    ...
    >>> sockets_manager = RealSocketsManager(...)
    >>> with sockets_manager:
    >>>     stream = sockets_manager.get_attack_stream()
    >>>     async def on_receive(attack):
    >>>         print(attack)
    >>>     await stream.subscribe_async(AsyncAnonymousObserver(on_receive))
    >>>     # 或者
    >>>     async for attack in AsyncIteratorObserver(stream):
    >>>         print(attack)
    """

    @inject
    def __init__(self, sockets: list[Socket], logger: Logger) -> None:
        self.sockets = sockets
        self.stream = AsyncSubject[Attack]()
        self.logger = logger
        self._tasks: list[asyncio.Task]

    async def _read_data_forever(self, socket: Socket):
        async def handle_data(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ):
            data = await reader.read()
            addr = writer.get_extra_info("peername")
            self.logger.info(f"received {data!r} on {addr}")

            attack = socket.attack_validator.validate(data).to_attack()

            await self.stream.asend(attack)

            writer.close()
            await writer.wait_closed()

        server = await asyncio.start_server(handle_data, socket.ip, socket.port)

        async with server:
            await server.serve_forever()

    @override
    def open_connections(self):
        self.logger.info("start opening connections")
        self._tasks = [
            asyncio.create_task(self._read_data_forever(socket))
            for socket in self.sockets
        ]

    @override
    def get_attack_stream(self):
        return self.stream

    @override
    def close_connections(self):
        self.logger.info("close connections")
        for task in self._tasks:
            task.cancel()
        asyncio.create_task(self.stream.aclose())

    def __enter__(self):
        self.open_connections()
        return self

    def __exit__(self, __exc_type, __exc_value, __traceback) -> bool | None:
        self.close_connections()
