from abc import ABC, abstractmethod
from schema import Attack, Socket
import asyncio
from injector import inject
from typing_extensions import override
from logger import Logger
from aioreactive import AsyncSubject, AsyncObservable


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
    


class RealSocketsManager(SocketsManager):
    """
    开启多个socket并同时接收数据，将接收的数据解析为`Attack`类并放入`self.message_queue`队列中 \n
    """
    @inject
    def __init__(self, sockets: list[Socket], logger: Logger) -> None:
        self.sockets = sockets
        self.stream = AsyncSubject[Attack]()
        self.logger = logger
        self._tasks: list[asyncio.Task]

    
    async def _read_data_forever(self, socket: Socket):
        async def handle_data(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
            data = await reader.read()
            addr = writer.get_extra_info('peername')
            self.logger.info(
                f"received {data!r} on {addr}"
            )
            
            attack = socket.attack_validator.validate(data).to_attack()
            
            await self.stream.asend(attack)

            writer.close()
            await writer.wait_closed()
            
        server = await asyncio.start_server(handle_data, socket.ip, socket.port)
        
        async with server:
            await server.serve_forever()
            
            
    @override
    def open_connections(self):
        # assert self._task
        self.logger.info("start opening connections")
        self._tasks = [asyncio.create_task(self._read_data_forever(socket)) for socket in self.sockets]
    
    
    @override
    def get_attack_stream(self):
        return self.stream
    
    
    @override
    def close_connections(self):
        self.logger.info("close connections")
        for task in self._tasks:
            task.cancel()
        asyncio.create_task(self.stream.aclose())
    
    
        


