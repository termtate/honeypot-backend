from asyncio import open_connection, Queue, create_task
from abc import ABC, abstractmethod
from schema import Attack, Socket
from sockets.decoder import decode
import asyncio
from injector import inject
from logging import getLogger, DEBUG
from typing_extensions import override

logger = getLogger(__name__)
logger.setLevel(DEBUG)

class SocketsManager(ABC):
    @abstractmethod
    async def get_attack_info(self) -> Attack: 
        pass
    @abstractmethod
    def open_connections(self) -> None: 
        pass
    @abstractmethod
    def close_connections(self) -> None: 
        pass
    


class RealSocketsManager(SocketsManager):
    """
    开启多个socket并同时接收数据，将接收的数据解析为`Attack`类并放入`self.message_queue`队列中 \n
    """
    @inject
    def __init__(self, sockets: list[Socket]) -> None:
        self.sockets = sockets
        self.message_queue = Queue[Attack]()
        self._tasks: list[asyncio.Task]

    
    async def _read_data_forever(self, socket: Socket):
        async def handle_data(reader: asyncio.StreamReader, writer):
            data = await reader.read()

            addr = writer.get_extra_info('peername')
            await self.message_queue.put(socket.attack_validator.validate(data).to_attack())

            writer.close()
            await writer.wait_closed()
            
        server = await asyncio.start_server(handle_data, socket.ip, socket.port)
        
        async with server:
            await server.serve_forever()
            
            
    @override
    def open_connections(self):
        # assert self._task
        logger.info("start opening connections")
        self._tasks = [asyncio.create_task(self._read_data_forever(socket)) for socket in self.sockets]
    
    
    @override
    async def get_attack_info(self) -> Attack:
        return await self.message_queue.get()
    
    
    @override
    def close_connections(self):
        logger.info("close connections")
        for task in self._tasks:
            task.cancel()
    
    
        


