import asyncio
from fastapi import WebSocket
from sockets import SocketsManager
from injector import inject, singleton
from logger import Logger
from aioreactive import AsyncIteratorObserver, AsyncAnonymousObserver
from schema import Attack
from core import Settings
import aioreactive as rx
from expression import pipe
from websocket.buffer import buffer


@singleton
class WebSocketManager:

    @inject
    def __init__(
        self, sockets_manager: SocketsManager, logger: Logger,
        settings: Settings
    ) -> None:
        self.websocket_connections: list[WebSocket] = []
        self.sockets_manager = sockets_manager
        self.logger = logger
        self._running_tasks: asyncio.Task | None = None
        self.interval = settings.WEBSOCKET_BUFFER_SEND_INTERVAL

    async def _start_listening_sockets(self):

        buffered_stream = await pipe(
            self.sockets_manager.get_attack_stream(),
            buffer(self.interval.seconds)
        )
        observer = rx.AsyncIteratorObserver(buffered_stream)

        async for attacks in observer:  # async for: 等待observer发送的attack，在收到attack时执行一轮循环，其他时间挂起，stream结束时退出循环
            text = str([attack.model_dump_json() for attack in attacks])
            await asyncio.gather(
                *[
                    websocket.send_text(text)
                    for websocket in self.websocket_connections
                ]
            )
            self.logger.info(
                f"send attacks to websockets {self.websocket_connections}"
            )

    def subscribe(self, websocket: WebSocket):
        if len(self.websocket_connections) == 0:
            assert self._running_tasks is None
            self._running_tasks = asyncio.create_task(
                self._start_listening_sockets()
            )

        self.websocket_connections.append(websocket)

    def remove(self, websocket: WebSocket):
        assert self._running_tasks is not None

        self.websocket_connections.remove(websocket)

        if len(self.websocket_connections) == 0:
            self._running_tasks.cancel()
            self._running_tasks = None
