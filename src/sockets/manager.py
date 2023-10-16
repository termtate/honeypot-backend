from asyncio import open_connection, Queue, create_task
from typing import Any, Literal, Protocol
from schema import Attack
from sockets.decoder import decode
import asyncio
from src.schema.socket import Socket
from injector import inject
from logging import getLogger, DEBUG

logger = getLogger(__name__)
# logger.setLevel(DEBUG)

class SocketsManager(Protocol):
    async def open_connections(self) -> None: ...
    async def get_attack_info(self) -> Attack: ...
    


class RealSocketsManager:
    """
    开启多个socket并同时接收数据，将接收的数据解析为`Attack`类并放入`self.message_queue`队列中 \n
    使用时，只需持续监听`self.message_queue`队列即可 \n
    """
    @inject
    def __init__(self, sockets: list[Socket]) -> None:
        self.sockets = sockets
        self.message_queue: Queue[Attack] = Queue()
        # self._tasks: list[asyncio.Task[bytes]] = []

    
    async def _read_data_forever(self, socket: Socket):
        reader, writer = await open_connection(
            host=socket.ip,
            port=socket.port
        )
        
        try:
            while True:
                # task = asyncio.create_task(reader.read())  # read until EOF
                # self._tasks.append(task)
                # data = await task
                # self._tasks.remove(task)
                data = await reader.read()
                await self.message_queue.put(decode(data))
        finally:
            writer.close()
            await writer.wait_closed()
            
    
    async def open_connections(self):
        """
        开启`sockets`的持续监听 \n
        注意，`open_connections()`内是死循环，直接调用会阻塞事件循环所在的线程，
        所以应该使用`asyncio.create_task()`将该协程交给事件循环调度执行
        """
        logger.info("start opening connections")
        await asyncio.gather(*[self._read_data_forever(socket) for socket in self.sockets])
    
    
    async def get_attack_info(self) -> Attack:
        return await self.message_queue.get()
    
    # def close(self):
    #     logger.info("close connections")
    #     for task in self._tasks:
    #         task.cancel()
    
    
        


